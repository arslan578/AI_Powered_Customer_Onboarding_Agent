# AI-Powered Customer Onboarding Agent

This project is an alpha version of an **AI-powered customer onboarding agent** built using **FastAPI**. The agent handles file uploads, performs data validation, transforms data, and securely communicates with a SaaS API.

## Features
- Accepts multiple file formats for upload: CSV, Excel, PDF, DOCX, and JSON.
- Validates and transforms uploaded data.
- Secure integration with an external SaaS API.
- API rate limiting to protect against abuse.
- JWT-based authentication for secure access to endpoints.
- Strong file handling practices to ensure security.

## Project Structure

```plaintext
AI_Powered_Customer_Onboarding_Agent/
│
├── app/                          # Core application directory
│   ├── api/                      # Contains API routes
│   ├── services/                 # Business logic and data validation
│   ├── utils/                    # Utility functions (file handling, logger, API clients)
│   ├── auth.py                   # Authentication and authorization logic
│   ├── mock_saas_api.py          # Mock SaaS API for testing integration
│   └── main.py                   # Main FastAPI app entry point
│
├── tests/                        # Unit and integration tests
│   └── test_file_upload.py       # Test cases for file upload API
│
├── Sample_files/                 # Sample files for testing uploads
│   ├── data.csv                  # Sample CSV file
│   ├── data.xlsx                 # Sample Excel file
│   ├── data.pdf                  # Sample PDF file
│   ├── data.json                 # Sample JSON file
│   └── data.docx                 # Sample DOCX file
│
├── .env                          # Environment variables (not included in the repo)
├── requirements.txt              # Project dependencies
└── README.md                     # This file
└── AI_Powered_Customer_Onboarding_Agent_api.postman_collection.json # Api Collection

```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/arslan578/AI_Powered_Customer_Onboarding_Agent.git
   cd AI_Powered_Customer_Onboarding_Agent
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   Create a `.env` file in the root directory and set the following variables:
   ```bash
   SECRET_KEY="your_jwt_secret_key"
   SAAS_API_KEY="your_mock_saas_api_key"
   SAAS_API_URL="server_url"
   ```

## Usage

1. **Run the FastAPI server:**
   ```bash
   uvicorn main:app --reload
   ```

2. **Access the API documentation:**
   Open your browser and navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to interact with the API using Swagger.

## Live Deployment

- **Live server URL:** https://ai-powered-customer-onboarding-agent.onrender.com/
- **Live API Docs:** https://ai-powered-customer-onboarding-agent.onrender.com/docs

## Endpoints

### `/signup` [POST]
Register a new user.

- Request:
  ```json
  {
    "username": "testuser",
    "password": "testpassword",
    "email": "testuser@example.com",
    "full_name": "Test User"
  }
  ```

### `/login` [POST]
Login to get a JWT token.

- Request:
  ```json
  {
    "username": "testuser",
    "password": "testpassword"
  }
  ```

### `/upload` [POST]
Upload a file for data validation and transformation.

- Supported file types: `CSV`, `Excel`, `PDF`, `DOCX`, `JSON`
- Requires authentication (Bearer Token)

- Response:
  ```json
  {
    "status": "Success",
    "message": "File uploaded, data validated, saved, and successfully sent to the SaaS platform."
  }
  ```

## Running Tests

1. **Run unit tests:**
   ```bash
   cd app/tests
   pytest test_file_upload.py
   ```

2. **Test authentication and file uploads:**
   - `test_file_upload.py` includes tests for signup, login, and file upload operations.

## Security Best Practices

- **File Handling:** Only accept specific file types and limit file size.
- **API Security:** JWT authentication and rate limiting are implemented to protect the API.
- **Environment Variables:** Sensitive information like API keys and JWT secrets are stored in environment variables.
  
## Future Improvements

- **Implement additional validation rules** for uploaded files.
- **Add more comprehensive unit tests** for different file types and edge cases.
- **Deploy the application** using Docker for better scalability and environment isolation.