from dotenv import load_dotenv


def load_environment_variables():
    """Load environment variables from .env file.

    This function loads environment variables from the .env file in the
    current directory.
    """
    load_dotenv("./.env")
