from pydantic import BaseModel, Field, ValidationError, validator


# Define the OnboardingDataModel using Pydantic for validation
class OnboardingDataModel(BaseModel):
    """
    Pydantic model for onboarding data validation.

    Attributes:
        name (str): The name of the user. It must contain only alphabetic characters and spaces.
        email (str): The email address of the user. It must follow a valid email pattern.
        age (int): The age of the user. It must be a positive integer.
    """

    name: str = Field(..., min_length=1,
                      description="Name must not be empty and must contain only alphabetic characters")
    email: str = Field(..., pattern=r"[^@]+@[^@]+\.[^@]+",
                       description="Email must follow a valid format (e.g., user@example.com)")
    age: int = Field(..., gt=0, description="Age must be a positive integer")

    # Validator for the 'name' field to ensure that only alphabetic characters and spaces are allowed
    @validator('name')
    def name_must_be_alpha(cls, v):
        """
        Custom validator for the 'name' field to ensure it only contains alphabetic characters and spaces.

        Args:
            v (str): The input value for the 'name' field.

        Returns:
            str: The validated value if it passes the check.

        Raises:
            ValueError: If the name contains non-alphabetic characters.
        """
        if not v.replace(" ", "").isalpha():
            raise ValueError('Name must contain only alphabetic characters and spaces')
        return v


# Function to validate data using the OnboardingDataModel
def validate_onboarding_data(data):
    """
    Function to validate onboarding data against the OnboardingDataModel.

    Args:
        data (dict): The dictionary containing the onboarding data (name, email, age).

    Returns:
        dict: The validated data in dictionary form.

    Raises:
        ValueError: If any of the data fields fail validation, a JSON-formatted validation error is raised.
    """
    try:
        # Validate the data against the OnboardingDataModel and return the validated data
        return OnboardingDataModel(**data).dict()
    except ValidationError as e:
        # Raise a ValueError with detailed validation error messages in JSON format
        raise ValueError(e.json())
