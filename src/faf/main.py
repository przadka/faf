# Standard library imports
import inspect
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List
from icecream import ic

# Related third party imports
import dotenv
from docstring_parser import parse
from litellm import completion

# Local application/library specific imports
from faf.tools import follow_up_then, save_url, note_to_self, va_request, journaling_topic

def get_tool_function_info(tool_func):
    # Parse the docstring using docstring-parser
    doc = parse(inspect.getdoc(tool_func))
    function_info = {
        "type": "function",
        "function": {
            "name": tool_func.__name__,
            "description": doc.short_description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }

    # Add parameters information
    sig = inspect.signature(tool_func)
    for name, param in sig.parameters.items():
        function_info["function"]["parameters"]["properties"][name] = {
            "type": "string",
            "description": next((p.description for p in doc.params if p.arg_name == name), "")
        }
        if param.default is inspect.Parameter.empty:
            function_info["function"]["parameters"]["required"].append(name)

    return function_info

def collect_functions_info(*funcs):
    return [get_tool_function_info(func) for func in funcs]


def tools_list():
    return collect_functions_info(
        follow_up_then, note_to_self, save_url, va_request, journaling_topic
    )

def call_tool_function(action):
    func_name = action['name']
    arguments = json.loads(action['arguments']) if isinstance(action['arguments'], str) else \
        action['arguments']
    tool_functions = {
        "follow_up_then": follow_up_then,
        "note_to_self": note_to_self,
        "save_url": save_url,
        "va_request": va_request,
        "journaling_topic": journaling_topic,
    }

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
    print("Writing to file: " + data)
    try:
        # Attempt to parse the JSON string to a dictionary
        data_dict = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(
            "Failed to decode 'data' from JSON. Ensure it is a properly formatted JSON string."
        ) from e

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

def improve_user_input(input_text: str, user_name: str, custom_rules, model: str) -> str:
    """
    Improve the user input before passing it to the LLM.

    Args:
        input_text (str): The user input text to improve.

    Returns:
        str: The improved user input text.
    """



    tools_list_str = ', '.join([item['function']['name'] for item in tools_list()])

    system_prompt = (
        "You are a helpful assistant tasked assiining the user's input to the relevant tool."
    )

    user_prompt = f"""

## Instructions
You are tasked with picking a relevant tool to process the user's input and add it to the
response, as #tool_name.

Here is a list of available tools: {tools_list_str}.

## Rules
- Focus only on assigning the user's input to the correct tool.
- Never add any new information or requests to the user's input.
- Never add any comments, observations, or opinions to the user's input when processing it.
- Never modify the user's input unless you are making spelling, grammar, or punctuation corrections.
- If the user mentions a day or date, ALWAYS use the 'follow_up_then' tool.
- If only a URL is provided, ALWAYS use the 'save_url' tool.
- Do not use follow_up_then if no date or time reference is provided.
- Use the 'va_request' tool ONLY if 'virtual assistant' or 'VA' is mentioned.
- Use the 'journaling_topic' tool ONLY if the user explicitly mentions journal or journaling.
- Journaling topics should be short and concise, with any relevant details included.
- If unsure which tool to use, just use the 'note_to_self' tool, passing the user's input
  as the message.
{custom_rules}

## Examples
Example 1:
Original: "I need to schle a meeting on this Thrusday."
Assistant output: "I need to schle a meeting on this Thrusday.. #follow_up_then"

Example 2:
Original: "Book a flught to New Yrk."
Assistant output:  "Book a flught to New Yrk. #note_to_self"

Example 3:
Original: "Vir asst, book a place for the AI coference."
Assistant output:  "Vir asst, book a place for the AI coference. #va_request"

Example 4:
Original: "I want to journal about my trip to the mountains."
Assistant output:  "I want to journal about my trip to the mountains. #journaling_topic"

## Task
Here is the user input you need to process:

===
{input_text}
===

Output full user input text and the relevant tool name. Nothing else.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response = completion(messages=messages, model= model)
        assistant_message = response.choices[0].message
    except Exception as e:
        return json.dumps({"error": "Failed to process input with LLM.", "details": str(e)})

    improved_text = assistant_message.content

    print("Text with tool: " + improved_text)
    return improved_text


def convert_to_json(
    request: str,
    user_name: str,
    custom_rules: str,
    model: str,
    tools_list: List[Dict[str, Any]],
) -> str:
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

    tools_names = [item['function']['name'] for item in tools_list if item['type'] == 'function']
    tools_names_str = ', '.join(tools_names)

    # Define the instructions for the LLM based on the given parameters
    system_prompt = f"""
You are a personal assistant, helping the user to manage their schedule and tasks.
You use various tools to process the user's requests and provide assistance.

You can have to FOLLOW THESE RULES srictly when responding to the user's input:

- User name is {user_name}. Avoid using it when responding directly to the user.
- Always try to only fix grammar, spelling, or punctuation mistakes in user's input
  before passing it to the tools.
- Never add any new information or requests to the user's input.
- Never add any comments, observations, or opinions to the user's input when processing it.
- If unsure which tool to use, just use the 'note_to_self' tool, passing the user's input
  as the message.
{custom_rules}
"""

    user_prompt = f"""
User provided the following input:

===
{request}
===

Use the following tools to process the user's request: {tools_names_str}.

You MUST use at least one tool to process the user's input. Do not include hashtag in your
input to tools.
"""

    # Structure the messages as required by the completion function
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Call the LLM completion function
    try:
        response = completion(messages=messages, model=model, tools=tools_list, temperature=0.1)
        assistant_message = response.choices[0].message
    except Exception as e:
        return json.dumps({"error": "Failed to process input with LLM.", "details": str(e)})

    # Extract content from the LLM response
    content = assistant_message.content
    if content:
        print('Assistant: ' + content)

    # Process tool calls from the LLM response
    try:
        actions = [
            {"name": arg.function.name, "arguments": arg.function.arguments}
            for arg in assistant_message.tool_calls
        ]
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
    Handles requests sent to AWS Lambda, converts the request into structured JSON, and
    processes it using specified tools.

    This function is designed to act as an interface for an AWS Lambda to handle inputs from
    external triggers (e.g., AWS API Gateway). It extracts the 'request' from the event object,
    validates it, and uses an LLM model to process the input.

    Parameters:
        event (dict): The event dictionary that AWS Lambda receives from the triggering service.
            It must contain:
            - 'request': a string representing the user input.
        context (LambdaContext): The runtime information provided by AWS Lambda, which is not
            used in this function but required by the signature.

    Returns:
        dict: A dictionary with the keys 'statusCode' and 'body'. The 'body' is a JSON string
            that represents:
            - The processed output when successful.
            - An error message when any part of the processing fails.

    The function checks for necessary environment variables, specifically:
        - OPENAI_API_KEY: Required for API access.
        - USER_NAME: Optional, defaults to 'unknown' if not set.

    It expects the Lambda environment to be configured with necessary models and tool
    configurations. Error responses follow typical HTTP status codes for ease of integration
    with HTTP-based APIs.

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
                'body': json.dumps(
                    'API Key not found. Please set your OPENAI_API_KEY environment variable.'
                ),
            }

        # Process the input to convert it to JSON
        improved_request = improve_user_input(request, USER_NAME, CUSTOM_RULES, MODEL)
        output = convert_to_json(improved_request, USER_NAME, CUSTOM_RULES, MODEL, tools_list())

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

    dotenv.load_dotenv()

    try:
        # Attempt to retrieve the user input from command line arguments
        try:
            request = sys.argv[1]
        except IndexError:
            print("No message provided. Exiting.")
            sys.exit(0)

        if not request:
            raise ValueError("No input provided. Please provide a message.")

        # Process the input to convert it to JSON

        # escape single and double quotes
        request = request.replace("'", "\\'").replace('"', '\\"')
        improved_request = improve_user_input(request, USER_NAME, CUSTOM_RULES, MODEL)

        output = convert_to_json(improved_request, USER_NAME, CUSTOM_RULES, MODEL, tools_list())

        if output:
            ic(output)
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
