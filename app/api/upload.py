import json
import docx
import pandas as pd
import pdfplumber
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from app.auth import get_current_user
from app.utils.api_client import send_data_to_saas_api
from app.utils.file_utils import save_and_validate_file
from app.services.validation import validate_onboarding_data
from app.utils.logger import log_error
from slowapi import Limiter

router = APIRouter()

# Initialize rate limiter
limiter = Limiter(key_func=lambda request: request.client.host)


@router.post("/upload")
@limiter.limit("5/minute")  # Limit requests to 5 per minute per client
async def upload_file(request: Request, file: UploadFile = File(...),
                      current_user: str = Depends(get_current_user)):
    """
    API endpoint to upload files, validate and transform data, and send it to the SaaS platform.
    - Only authenticated users can access this endpoint (enforced by JWT token).
    - The supported file types are CSV, Excel, JSON, PDF, and DOCX.

    Args:
        request: FastAPI request object.
        file: Uploaded file (validated for specific formats).
        current_user: Current user fetched through JWT authentication.

    Returns:
        A JSON response with status and message, including response from the SaaS API if successful.

    Raises:
        HTTPException: For unsupported file types, validation errors, or any internal errors.
    """
    try:
        # Save and validate the uploaded file
        file_path = await save_and_validate_file(file)

        # Process the file content based on the file type
        if file.content_type == 'application/json':
            onboarding_data = pd.read_json(file_path)
            onboarding_data = onboarding_data.to_dict(orient='records')
        elif file.content_type == 'text/csv':
            onboarding_data = pd.read_csv(file_path).to_dict(orient='records')
        elif file.content_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            onboarding_data = pd.read_excel(file_path).to_dict(orient='records')
        elif file.content_type == 'application/pdf':  # Handle PDF files
            onboarding_data = await handle_pdf(file_path)
        elif file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':  # Handle DOCX
            onboarding_data = await handle_docx(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Validate the extracted data
        validated_data = []
        for entry in onboarding_data:
            try:
                # Validate each entry using the defined onboarding data model
                validated_entry = validate_onboarding_data(entry)
                validated_data.append(validated_entry)
            except ValueError as e:
                # Log validation errors and raise an exception
                log_error(e)
                raise HTTPException(status_code=400, detail=f"Validation error in {json.loads(e.args[0])[0]['loc'][0]} column data")

        # Send the validated data to the SaaS platform
        response = await send_data_to_saas_api(validated_data)

        # Return success response if data is validated and sent successfully
        return {
            "status": "Success",
            "message": "File uploaded, data validated, saved, and successfully sent to the SaaS platform.",
            "saas_api_response": response  # Optional: include SaaS API response
        }

    except Exception as e:
        # Log any unexpected errors and raise an HTTPException
        log_error(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Helper function to handle PDF files
async def handle_pdf(file_path: str):
    """
    Helper function to extract data from a PDF file.
    The function assumes that the PDF contains a structured format with columns like name, email, and age.

    Args:
        file_path: Path to the uploaded PDF file.

    Returns:
        A list of dictionaries containing extracted and structured data (name, email, age).

    Raises:
        HTTPException: If no valid data is found or there's an error during extraction.
    """
    try:
        extracted_data = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    # Process each line based on structure
                    for line in lines:
                        # Skip headers and empty lines
                        if line.strip().lower().startswith('name') or not line.strip():
                            continue

                        # Use regular expression to capture email and age, assuming age is at the end
                        columns = line.split()
                        email_idx = next((i for i, word in enumerate(columns) if "@" in word), -1)

                        if email_idx != -1 and len(columns) > email_idx + 1:
                            # Reconstruct name from all parts before the email
                            name = " ".join(columns[:email_idx])
                            email = columns[email_idx]
                            # Extract the age (last column)
                            age = columns[email_idx + 1]
                            if re.match(r'^\d+$', age):  # Ensure age is a valid number
                                extracted_data.append({"name": name, "email": email, "age": int(age)})

        if not extracted_data:
            raise HTTPException(status_code=400, detail="No valid data found in the PDF")
        return extracted_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF file: {str(e)}")


# Helper function to handle DOCX files
async def handle_docx(file_path: str):
    """
    Helper function to extract data from a DOCX file.
    Assumes the DOCX file contains structured tables with columns: name, email, and age.

    Args:
        file_path: Path to the uploaded DOCX file.

    Returns:
        A list of dictionaries containing extracted and structured data (name, email, age).

    Raises:
        HTTPException: If no valid data is found or there's an error during extraction.
    """
    try:
        # Load the DOCX file
        doc = docx.Document(file_path)
        extracted_data = []

        # Process each table (assuming the first table has the data)
        for table in doc.tables:
            for i, row in enumerate(table.rows):
                # Skip the header row
                if i == 0:
                    continue

                # Extract name, email, and age from the table's columns
                name = row.cells[0].text.strip()
                email = row.cells[1].text.strip()
                age = row.cells[2].text.strip()

                # Ensure age is numeric
                if age.isdigit():
                    extracted_data.append({
                        "name": name,
                        "email": email,
                        "age": int(age)
                    })

        if not extracted_data:
            raise HTTPException(status_code=400, detail="No valid data found in the DOCX file")
        return extracted_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing DOCX file: {str(e)}")
