import json
import os


def load_text_file(filepath: str):
    """Loads the contents of a text file at the given filepath.

    Args:
        filepath: The path to the text file to load.

    Returns:
        The contents of the text file as a string.

    Raises:
        FileNotFoundError: If the file is not found.
    """
    if not (os.path.exists(filepath) or os.path.isfile(filepath)):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r") as f:
        return f.read()


def load_json_file(filepath: str):
    """Loads the contents of a JSON file at the given filepath.

    Args:
        filepath: The path to the JSON file to load.

    Returns:
        The contents of the JSON file as a Python object.

    Raises:
        FileNotFoundError: If the file at the given filepath does not exist.
    """
    if not (os.path.exists(filepath) or os.path.isfile(filepath)):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r") as f:
        return json.load(f)
