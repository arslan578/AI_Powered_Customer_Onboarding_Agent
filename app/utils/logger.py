import logging

# Configure the logging settings
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO or higher
logger = logging.getLogger(__name__)  # Create a logger instance with the current module's name

def log_error(error):
    """
    Logs an error message using the logger.

    This function accepts an error object or message and logs it at the ERROR level,
    allowing the developer to capture important errors in the application for debugging purposes.

    Args:
        error (Exception or str): The error message or Exception object that needs to be logged.
    """
    # Log the error message at the ERROR level
    logger.error(f"Error: {error}")
