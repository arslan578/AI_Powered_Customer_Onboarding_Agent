import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv  # Import dotenv to load environment variables

# OAuth2PasswordBearer dependency for getting token from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load environment variables from .env file (e.g., SECRET_KEY)
load_dotenv()

# Secret key for JWT signing (should be stored securely in production)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"  # Algorithm used for JWT encoding
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes

# Context for password hashing using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user storage for demo purposes
fake_users_db = {}

# Pydantic models to represent users and tokens
class User(BaseModel):
    """
    Represents the public user data (without password).
    """
    username: str
    email: str
    full_name: Optional[str] = None


class UserInDB(User):
    """
    Represents the user in the database, including the hashed password.
    """
    hashed_password: str


class UserCreate(BaseModel):
    """
    Model for creating a new user with a plaintext password.
    """
    username: str
    email: str
    full_name: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    """
    Model for user login credentials.
    """
    username: str
    password: str


class Token(BaseModel):
    """
    Represents a JWT token response.
    """
    access_token: str
    token_type: str


# Utility function to hash passwords
def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password (str): The plaintext password to be hashed.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


# Utility function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that the provided plaintext password matches the stored hashed password.

    Args:
        plain_password (str): The plaintext password to check.
        hashed_password (str): The stored hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# Utility function to create a JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token for the given user data.

    Args:
        data (dict): The user data to encode into the token.
        expires_delta (Optional[timedelta]): The expiration time of the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # Encode the JWT using the SECRET_KEY and HS256 algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Utility function to authenticate a user
def authenticate_user(db: dict, username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user by verifying their username and password.

    Args:
        db (dict): The database of users (in-memory).
        username (str): The username to authenticate.
        password (str): The plaintext password to verify.

    Returns:
        Optional[UserInDB]: The authenticated user if successful, otherwise None.
    """
    user = db.get(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Utility function to verify and decode a JWT token
def verify_token(token: str) -> str:
    """
    Verify and decode the JWT token to extract the username.

    Args:
        token (str): The JWT token.

    Returns:
        str: The username extracted from the token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency function to get the current user based on the JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependency to get the current user from the token.

    Args:
        token (str): The JWT token from the request header.

    Returns:
        str: The username of the authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user cannot be authenticated.
    """
    return verify_token(token)
