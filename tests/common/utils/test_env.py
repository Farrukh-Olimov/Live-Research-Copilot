import os


def test_load_environment_variables():
    """Test that loads environment variables from .env file.

    This test ensures that the load_environment_variables() function loads
    environment variables from the .env file in the current directory.
    """
    from common.utils.env import load_environment_variables

    env_variables = os.environ.copy()
    load_environment_variables()
    assert env_variables != os.environ, "Environment variables not loaded"
