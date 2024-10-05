from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import List

# Create an APIRouter instance for the mock SaaS API
router = APIRouter()

# Define the expected data format for each customer
class CustomerData(BaseModel):
    """
    Pydantic model to represent individual customer data.

    Attributes:
        name (str): The name of the customer.
        email (str): The email of the customer.
        age (int): The age of the customer.
    """
    name: str
    email: str
    age: int

# Mock API key for authentication
MOCK_API_KEY = "cQb1fAf7rzwYGw4Kw4qGekpm8uOvv3nA"

# Define a model to handle the array of customer data
class CustomerDataArray(BaseModel):
    """
    Pydantic model to represent an array of customer data entries.

    Attributes:
        data (List[CustomerData]): A list of customer data entries.
    """
    data: List[CustomerData]

@router.post("/api/saas/submit")
async def submit_data(data: CustomerDataArray, x_api_key: str = Header(...)):
    """
    Mock SaaS API endpoint to receive customer data.

    This endpoint accepts an array of customer data, validates the API key, and
    simulates processing the received data.

    Args:
        data (CustomerDataArray): The array of customer data submitted in the request.
        x_api_key (str): The API key submitted in the request header for authentication.

    Returns:
        dict: A success message indicating that the data was received and processed.

    Raises:
        HTTPException: If the API key is invalid, an HTTP 401 Unauthorized error is raised.
    """
    # Validate the provided API key
    if x_api_key != MOCK_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Simulate successful processing of the data
    print("Received the following data:", data.dict())

    # Return a success message with the received data
    return {
        "status": "success",
        "message": "Data received successfully",
        "data": data
    }
