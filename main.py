from datetime import timedelta
from fastapi import FastAPI, Request, HTTPException, status, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse

from app.api.upload import router as upload_router  # Importing the file upload router
from app.auth import (
    UserLogin, User, UserCreate, fake_users_db, get_password_hash, UserInDB, Token, authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
)  # Importing authentication utilities and models
from app.mock_saas.mock_saas_api import router as mock_saas_api_router  # Importing the mock SaaS API router

# Initialize rate limiter with a key function that uses the request's remote address for rate limiting
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI()

# Set the rate limit exceeded handler for the app
# This handles responses when the rate limit is exceeded (HTTP status code 429)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# Register API routers
app.include_router(upload_router)  # File upload functionality
app.include_router(mock_saas_api_router)  # Mock SaaS API functionality


@app.post("/signup", response_model=User)
def signup(user: UserCreate):
    """
    Endpoint to register a new user.

    This function checks if the username already exists, hashes the password, and stores the user in an
    in-memory database (`fake_users_db`). If the username is already taken, it raises an HTTP 400 error.

    Args:
        user (UserCreate): The user data including username, password, email, and optional full name.

    Returns:
        UserInDB: The user data stored in the database without the plaintext password.

    Raises:
        HTTPException: If the username already exists.
    """
    # Check if the username is already registered
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password and store the user in the in-memory database
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(**user.dict(), hashed_password=hashed_password)
    fake_users_db[user.username] = user_in_db

    return user_in_db  # Return the created user


@app.post("/login", response_model=Token)
def login(user: UserLogin):
    """
    Endpoint for user login and JWT token generation.

    This function authenticates the user by verifying the provided username and password. If the credentials
    are correct, a JWT access token is generated and returned. If authentication fails, an HTTP 401 error is raised.

    Args:
        user (UserLogin): The login credentials (username and password).

    Returns:
        Token: A JSON Web Token (JWT) containing the access token and token type.

    Raises:
        HTTPException: If the credentials are incorrect.
    """
    # Authenticate the user using the provided username and password
    user_in_db = authenticate_user(fake_users_db, user.username, user.password)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate a JWT token with an expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user_in_db.username}, expires_delta=access_token_expires)

    # Return the generated token
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/limited")
@limiter.limit("10/minute")  # Apply a rate limit of 10 requests per minute to this endpoint
async def limited_route(request: Request):
    """
    A sample endpoint to demonstrate rate limiting.

    This endpoint is limited to 10 requests per minute for each user based on their IP address.
    If the limit is exceeded, the request will receive a 429 (Too Many Requests) response.

    Args:
        request (Request): The request object (required by the rate limiter).

    Returns:
        JSONResponse: A message indicating the rate-limited route.
    """
    return JSONResponse(content={"message": "This is a rate-limited route"})
