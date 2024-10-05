import os
import aiohttp
from fastapi import HTTPException
from dotenv import load_dotenv  # Import dotenv to load .env variables

# Load environment variables from .env file
load_dotenv()

# Retrieve SaaS API key and URL from environment variables
SaaS_API_KEY = os.getenv("SaaS_API_KEY")
SAAS_API_URL = os.getenv("SAAS_API_URL")

# Construct the full SaaS API URL by appending the submit endpoint
MOCK_SAAS_API_URL = f"{SAAS_API_URL}/api/saas/submit"

async def send_data_to_saas_api(data):
    """
    Function to send validated onboarding data to the mock SaaS API.

    This function uses an asynchronous HTTP session to send the POST request with
    the customer data in a JSON format to the SaaS API. The API key is included
    in the request headers for authentication. If the request is unsuccessful,
    it raises an HTTP exception.

    Args:
        data (list): A list of customer data dictionaries to be sent to the SaaS API.

    Returns:
        dict: The JSON response from the SaaS API, containing the status of the request.

    Raises:
        HTTPException: If the API key is invalid, or if there's an issue communicating
                       with the SaaS API (e.g., network errors or server errors).
    """
    async with aiohttp.ClientSession() as session:
        # Prepare the headers, including the API key
        headers = {
            "x-api-key": SaaS_API_KEY
        }
        try:
            # Wrap the data into a dictionary with the key "data"
            payload = {"data": data}

            # Send a POST request to the SaaS API with the data
            async with session.post(MOCK_SAAS_API_URL, json=payload, headers=headers) as response:
                # Check if the response status is not 200 (OK)
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Error communicating with SaaS API")

                # Return the JSON response from the SaaS API
                return await response.json()

        except Exception as e:
            # Raise an HTTPException if an error occurs while sending the data
            raise HTTPException(status_code=500, detail=f"Failed to connect to SaaS API: {str(e)}")
