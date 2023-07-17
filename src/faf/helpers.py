import os

def get_env_var(var_name: str) -> str:
    """
    Get the value of the environment variable var_name.

    Args:
        var_name: The name of the environment variable.

    Returns:
        The value of the environment variable.

    Raises:
        EnvironmentError: If the environment variable is not set.
    """
    value = os.environ.get(var_name)
    if value is None:
        raise EnvironmentError(f"{var_name} is not set")

    return value

def validate_user_input(input):
    """
    Validate the user input.

    Args:
        input: The user input.

    Returns:
        True if the input is valid, False otherwise.

    Raises:
        ValueError: If the input is not valid.
    """
    if not input:
        raise ValueError("No input provided. Please provide a message.")

    return True
