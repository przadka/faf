import sys
import json
import os
import dotenv
from datetime import datetime
from typing import List, Dict, Any

from litellm import completion
from tools import follow_up_then, user_note, save_url, va_request


def tools_list():
    """
        Generate a list of tools available for the LLM to use.
    """

    tools_list = [{
        "type": "function",
        "function": {
            "name": "follow_up_then",
            "description": """Send a follow-up reminder with the given date and message. Use only if there is a specific date provided or some time reference like "tomorrow" or "in 2 days".
    Additional constraints for the date:

    - Do not use "this" in the date like "thisMonday" or "thisTuesday" as FUT does not support them.
    - Do not use "inaweek", "in2weeks" or "in1month" replace them with "1week",  "2weeks" and "1month" respectively. 
    - Date cannot have any spaces, dots or commas.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Full prompt provided by the user."
                    },
                    "date": {
                        "type": "string",
                        "description": "Date of the follow-up in the format like '1August', 'tomorrow3pm' or '2weeks'."
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to send."
                    }
                },
                "required": ["prompt", "date", "message"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "user_note",
            "description": """Send a note to user with the given message. Useful for simple todos, reminders and short-term follow ups.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Full prompt provided by the user."
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to send."
                    }
                },
                "required": ["prompt", "message"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "save_url",
            "description": """Save a URL to a URL list so that I can review it later. Use only if the input is a valid URL.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Full prompt provided by the user."
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to append to the URL list."
                    }
                },
                "required": ["prompt", "url"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "va_request",
            "description": """Request for virtual assistant. Use only if the input explicitly includes the word "virtual assistant" or "VA".""",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Full prompt provided by the user."
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the request, used as a Trello card title. Keep it short."
                    },
                    "request": {
                        "type": "string",
                        "description": "Request to send to the virtual assistant."
                    }
                },
                "required": ["prompt", "title", "request"]
            }
        }
    }
    ]

    return tools_list

def call_tool_function(action):
    func_name = action['name']
    arguments = json.loads(action['arguments']) if isinstance(action['arguments'], str) else action['arguments']
    tool_functions = {"follow_up_then": follow_up_then, "user_note": user_note, "save_url": save_url, "va_request": va_request}
    
    if func_name in tool_functions:
        print(f"Calling {func_name} with arguments: ", arguments)
        return {
            "tool_call_name": func_name,
            "output": tool_functions[func_name](**arguments)
        }
    else:
        raise ValueError(f"Unknown function: {func_name}")

def write_to_file(data: str) -> str:
    """
    Writes the provided JSON string to a file in a specified output directory.

    Args:
        data (str): JSON string to write to the file.

    Returns:
        str: Success message with the filename and directory where the file is saved.
    
    Raises:
        ValueError: If the data is not a valid JSON string.
    """
    try:
        # Attempt to parse the JSON string to a dictionary
        data_dict = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError("Failed to decode 'data' from JSON. Ensure it is a properly formatted JSON string.") from e

    # Determine the output directory, defaulting to the current file's directory if not set
    directory = os.getenv('FAF_JSON_OUTPUT_PATH', os.path.dirname(os.path.abspath(__file__)))

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Generate a unique filename using the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{data_dict.get('command', 'unknown')}.json"

    # Construct the full path for the file
    file_path = os.path.join(directory, filename)

    # Write the data to the file
    try:
        with open(file_path, 'w') as outfile:
            json.dump(data_dict, outfile)
    except IOError as e:
        raise IOError(f"Unable to write to the file {filename}.") from e

    return f"Success: Data written to {filename} in directory {directory}."



def convert_to_json(request: str, user_name: str, custom_rules: str, model: str, tools_list: List[Dict[str, Any]]) -> str:
    """
    Converts user requests into structured JSON using predefined LLM rules and functions.

    Args:
        request (str): The user input string.
        user_name (str): The username fetched from the environment.
        custom_rules (str): Additional rules loaded from a file.
        model (str): The model identifier for the LLM.
        tools_list (list): List of tools available for the LLM to use.

    Returns:
        str: A JSON string of the processed output including metadata.
    """
    # Define the instructions for the LLM based on the given parameters
    instructions = f"""
    You are a personal assistant, helping the user to manage their schedule and tasks.
    You use various tools to process follow ups, set reminders, collect URLs and contact the personal assistant.
    
    - User name is {user_name}.
    - NEVER add any new information or requests to the user's input.
    - Correct only grammar, spelling, or punctuation mistakes.
    - Use correct grammar and punctuation.
    - If the user mentions a day or date, ALWAYS use the 'follow_up_then' tool.
    - If only a URL is provided, ALWAYS use the 'save_url' tool.
    - Use the 'va_request' tool ONLY if 'virtual assistant' or 'VA' is mentioned.
    - Use the 'user_note' tool if unsure which tool to apply or if others fail.
    {custom_rules}
    """

    # Structure the messages as required by the completion function
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": request}
    ]

    # Call the LLM completion function
    try:
        response = completion(messages=messages, model=model, tools=tools_list)
        assistant_message = response.choices[0].message
    except Exception as e:
        return json.dumps({"error": "Failed to process input with LLM.", "details": str(e)})

    # Extract content from the LLM response
    content = assistant_message.content
    if content:
        print('Assistant: ' + content)

    # Process tool calls from the LLM response
    try:
        actions = [{"name": arg.function.name, "arguments": arg.function.arguments} for arg in assistant_message.tool_calls]
        tool_outputs = [call_tool_function(action) for action in actions]
        output = tool_outputs[0]['output']
        output = json.loads(output)
    except Exception as e:
        return json.dumps({"error": "Failed to execute tool functions.", "details": str(e)})

    # Add metadata to the output
    output.update({
        'created': response.created,
        'model': response.model,
        'prompt_tokens': response.usage.prompt_tokens,
        'completion_tokens': response.usage.completion_tokens,
        'total_tokens': response.usage.total_tokens
    })

    return output

def load_configuration():

    dotenv.load_dotenv()

    MODEL = os.getenv("FAF_MODEL") or "gpt-4-1106-preview"
    USER_NAME = os.getenv("FAF_USER_NAME") or "Unknown"
    CUSTOM_RULES_FILE = os.getenv("FAF_CUSTOM_RULES_FILE") or ""

    CUSTOM_RULES = ""
    
    try:
        with open(CUSTOM_RULES_FILE, "r") as file:
            CUSTOM_RULES = file.read()
    except FileNotFoundError:
        CUSTOM_RULES_FILE = None
    
    return MODEL, USER_NAME, CUSTOM_RULES

def lambda_handler(event, context):
    """
    Handles requests sent to AWS Lambda, converts the request into structured JSON, and processes it using specified tools.

    This function is designed to act as an interface for an AWS Lambda to handle inputs from external triggers (e.g., AWS API Gateway).
    It extracts the 'request' from the event object, validates it, and uses an LLM model to process the input.

    Parameters:
        event (dict): The event dictionary that AWS Lambda receives from the triggering service. It must contain:
                      - 'request': a string representing the user input.
        context (LambdaContext): The runtime information provided by AWS Lambda, which is not used in this function but required by the signature.

    Returns:
        dict: A dictionary with the keys 'statusCode' and 'body'. The 'body' is a JSON string that represents:
              - The processed output when successful.
              - An error message when any part of the processing fails.

    The function checks for necessary environment variables, specifically:
        - OPENAI_API_KEY: Required for API access.
        - USER_NAME: Optional, defaults to 'unknown' if not set.

    It expects the Lambda environment to be configured with necessary models and tool configurations.
    Error responses follow typical HTTP status codes for ease of integration with HTTP-based APIs.

    Examples of `event` structure:
        {'request': 'Your request string here'}
    """

    MODEL, USER_NAME, CUSTOM_RULES = load_configuration()

    try:
        # Extract the request from the Lambda event
        request = event.get('request')
        if not request:
            return {
                'statusCode': 400,
                'body': json.dumps('No input provided. Please provide a message.')
            }

        # Check for the necessary API key in environment variables
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {
                'statusCode': 403,
                'body': json.dumps('API Key not found. Please set your OPENAI_API_KEY environment variable.')
            }

        # Process the input to convert it to JSON
        output = convert_to_json(request, USER_NAME, CUSTOM_RULES, MODEL, tools_list())

        return {
            'statusCode': 200,
            'body': json.dumps(output)
        }

    except ValueError as ve:
        return {
            'statusCode': 400,
            'body': json.dumps(str(ve))
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"An unexpected error occurred: {str(e)}")
        }

def main():

    MODEL, USER_NAME, CUSTOM_RULES = load_configuration()

    try:
        # Attempt to retrieve the user input from command line arguments
        try:
            request = sys.argv[1]
        except IndexError:
            print("No message provided. Exiting.")
            sys.exit(0)

        if not request:
            raise ValueError("No input provided. Please provide a message.")

        # Check for the necessary API key in environment variables
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API Key not found. Please set your OPENAI_API_KEY environment variable.")

        # Process the input to convert it to JSON
        output = convert_to_json(request, USER_NAME, CUSTOM_RULES, MODEL, tools_list())

        # If there's output, print it prettily
        if output:
            write_to_file(json.dumps(output))

    except ValueError as ve:
        print(str(ve))
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("Please set the necessary environment variables and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
