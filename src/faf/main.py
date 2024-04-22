import sys
import time
from openai import OpenAI
import json
import os
import dotenv
from helpers import get_env_var, validate_user_input
from tools import follow_up_then, user_note, save_url, va_request

# Load environment variables
dotenv.load_dotenv()

# Constants
OPENAI_MODEL = "gpt-4-1106-preview"

# Load user name and custom rules
USER_NAME = get_env_var("FAF_USER_NAME") or "unknown"

# Load custom rules md file, default to None if not set
try:
    CUSTOM_RULES_FILE = get_env_var("FAF_CUSTOM_RULES_FILE")
    with open(CUSTOM_RULES_FILE, "r") as file:
        custom_rules = file.read()
except OSError:
    CUSTOM_RULES_FILE = None
    custom_rules = ""
 
def call_tool_function(action):
    func_name = action['name']
    arguments = json.loads(action['arguments']) if isinstance(action['arguments'], str) else action['arguments']
    tool_functions = {"follow_up_then": follow_up_then, "user_note": user_note, "save_url": save_url, "va_request": va_request}
    
    if func_name in tool_functions:
        print(f"Calling {func_name} with arguments: ", arguments)
        return {
            "tool_call_id": action['id'],
            "output": tool_functions[func_name](**arguments)
        }
    else:
        raise ValueError(f"Unknown function: {func_name}")




tools_list = [{
    "type": "function",
    "function": {
        "name": "follow_up_then",
        "description": """Send a follow-up reminder with the given date and message. Use only if there is a specific date provided or some time reference like "tomorrow" or "in 2 days".
Additional contraits for the date:

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

def main():
    try:
        # Check that the necessary environment variables are set
        
        request = sys.argv[1]
        validate_user_input(request)
        print("Current prompt: ", request, "\n")

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("API Key not found. Please set your OPENAI_API_KEY environment variable.")


        instructions = f"""
You are a personal assistant, helping the user to manage their schedule and tasks. You use various tools to process follow ups, set reminders, collect URLs and contact personal assistant.

You MUST obey the following rules when responding to the user's input:

- User name is {USER_NAME}.
- The user will sometimes talk as if they were giving instructions to you, but in fact they want you to send these instructions to them, either as reminders or follow ups etc.
- NEVER add any new information or new requests to the user's input. Correct only grammar, spelling, or punctuation mistakes.
- Never replace user input with URLs or other links.
- Use correct grammar and punctuation. Speak in a friendly and professional manner, with full sentences.
- If the user mentions a day of the week, or an exact date, then ALWAYS use the follow_up_then tool.
- Always perform action on the user input and send the result back to the user.
- If only URL is provided, then ALWAYS use the save_url tool.
- Use the va_request tool ONLY if the user explicitly includes the word "virtual assistant" or "VA" in the prompt.
- If unsure which tool to use, then use the user_note tool.
- If other tools fail, then use the user_note tool.
{custom_rules if CUSTOM_RULES_FILE else ""}
"""

        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": request}
        ]

        client = OpenAI()

        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            tools = tools_list

        )

        assistant_message = response.choices[0].message
        content = assistant_message.content
        tc = assistant_message.tool_calls[0].function.arguments
        actions = [arg.function.name for arg in assistant_message.tool_calls]
        print(actions)
        # print("Assistant: ", content)
        # print(tc)

        # tool_outputs = [call_tool_function(action) for action in required_actions["tool_calls"]]


    except IndexError:
        print("No message provided. Exiting.")
        exit(0)
    except ValueError as e:
        print(str(e))
        exit(1)
    except EnvironmentError as e:
        print(str(e))
        print("Please set the necessary environment variables and try again.")
        exit(1)



if __name__ == "__main__":
    main()