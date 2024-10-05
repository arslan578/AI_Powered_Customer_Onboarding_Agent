import pytest
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app from main.py

# Initialize TestClient to make HTTP requests to your FastAPI app
client = TestClient(app)


@pytest.fixture
def signup():
    """
    Fixture to sign up a new user.

    This function sends a POST request to the '/signup' endpoint to register a new user
    and ensures the signup is successful with a status code 200. The signed-up user data
    is returned as a JSON response.

    Returns:
        dict: JSON response containing the user details.
    """
    signup_data = {
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com",
        "full_name": "Test User"
    }

    response = client.post("/signup", json=signup_data)
    assert response.status_code == 200  # Ensure signup is successful
    return response.json()


@pytest.fixture
def get_token(signup):
    """
    Fixture to log in and retrieve a JWT token.

    This function logs in the user that was signed up using the `signup` fixture.
    It sends a POST request to the '/login' endpoint, retrieves the JWT access token
    if the login is successful, and ensures the status code is 200.

    Args:
        signup (fixture): The fixture to sign up a user (ensures the user is created before login).

    Returns:
        str: The JWT access token for the logged-in user.
    """
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }

    # Send login request to obtain the token
    response = client.post("/login", json=login_data)
    assert response.status_code == 200  # Ensure login is successful
    token = response.json()["access_token"]  # Extract the JWT token
    return token


def test_signup_login_and_upload_csv(get_token):
    """
    Test case to validate the entire process: user signup, login, and CSV file upload.

    This function:
    - Signs up a new user using the `signup` fixture.
    - Logs in and retrieves a JWT token using the `get_token` fixture.
    - Uploads a CSV file using the '/upload' endpoint while authenticated with the JWT token.

    Args:
        get_token (fixture): The JWT token retrieved from the `get_token` fixture.

    Assertions:
        - Ensure the status code is 200 after the file upload.
        - Ensure the 'message' field is present in the response and has the expected success message.
    """
    # Get the JWT token
    token = get_token

    # Path to a sample CSV file within your test directory (ensure you have this file in 'files/data.csv')
    with open("files/data.csv", "rb") as file:
        response = client.post(
            url="/upload",
            headers={"Authorization": f"Bearer {token}"},  # Include token in Authorization header
            files={"file": file}
        )

        # Assertions to ensure the API call was successful
        assert response.status_code == 200  # Ensure the status code is OK
        assert "message" in response.json()  # Check for the 'message' key in the response
        assert response.json()[
                   "message"] == "File uploaded, data validated, saved, and successfully sent to the SaaS platform."
