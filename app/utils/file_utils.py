import os
from fastapi import HTTPException, UploadFile
from pathlib import Path
import time

# Define the upload directory relative to the current working directory
UPLOAD_DIR = Path("uploads/")

async def save_and_validate_file(file: UploadFile):
    """
    Save and validate an uploaded file.

    This function saves the uploaded file to the `uploads/` directory after validating
    its file extension. If a file with the same name exists, it appends a timestamp
    to the filename to make it unique.

    Args:
        file (UploadFile): The file uploaded via FastAPI's `UploadFile`.

    Returns:
        Path: The path to the saved file.

    Raises:
        HTTPException: If the file extension is not supported.
    """
    # Create the upload directory if it doesn't exist
    if not UPLOAD_DIR.exists():
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Create the directory, including parent directories

    # Sanitize the file name to avoid directory traversal attacks
    filename = os.path.basename(file.filename)
    file_path = UPLOAD_DIR / filename

    # Validate file extension to only allow specific formats
    if file_path.suffix not in ['.csv', '.xlsx', '.pdf', '.docx', '.json']:
        # Raise an exception if the file type is not supported
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Check if a file with the same name already exists
    if file_path.exists():
        # Append a timestamp to the file name to ensure uniqueness
        timestamp = int(time.time())
        new_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        file_path = UPLOAD_DIR / new_filename

    # Save the file securely by writing its contents to the determined file path
    with open(file_path, "wb") as buffer:
        # Read the uploaded file and write it to the designated location
        buffer.write(await file.read())

    # Return the path of the saved file
    return file_path
