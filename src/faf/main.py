import sys
import time
import openai
import json
import os
import dotenv
from datetime import datetime


from tools import follow_up_then, user_note, save_url, va_request

# Load environment variables
dotenv.load_dotenv()

# Configuration
OPENAI_MODEL = "gpt-4-1106-preview"
USER_NAME = os.getenv("FAF_USER_NAME") or "unknown"
custom_rules = ""

try:
    CUSTOM_RULES_FILE = os.getenv("FAF_CUSTOM_RULES_FILE")
    
    with open(CUSTOM_RULES_FILE, "r") as file:
        custom_rules = file.read()
except OSError:
    CUSTOM_RULES_FILE = None

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
def call_tool_function(action):
    func_name = action['function']['name']
    arguments = json.loads(action['function']['arguments']) if isinstance(action['function']['arguments'], str) else action['function']['arguments']
    tool_functions = {"follow_up_then": follow_up_then, "user_note": user_note, "save_url": save_url, "va_request": va_request}
    
    if func_name in tool_functions:
        print(f"Calling {func_name} with arguments: ", arguments)
        return {
            "tool_call_id": action['id'],
            "output": tool_functions[func_name](**arguments)
        }
    else:
        raise ValueError(f"Unknown function: {func_name}")


def write_to_file(data: str) -> str:
    """
    Write the data to a JSON file in the output directory.

    Args:
        data: JSON string to write to the file.
    
    Returns:
        Success message with the filename and directory where the file is saved.
    """
    try:
        data_dict = json.loads(data)
    except json.JSONDecodeError:
        return "Error: Failed to decode 'data' from JSON. Ensure it is a properly formatted JSON string."

    # Get the output directory from environment variable, default to current file's directory
    directory = os.getenv('FAF_JSON_OUTPUT_PATH', os.path.dirname(os.path.abspath(__file__)))

    # Create directory if it does not exist
    os.makedirs(directory, exist_ok=True)

    # Use current timestamp to generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{data_dict.get('command', 'unknown')}.json"

    # Write the data to the file
    with open(os.path.join(directory, filename), 'w') as outfile:
        json.dump(data_dict, outfile)
        
    return f"Success: Data written to {filename} in directory {directory}."


def main():
    faf_output = ""
    try:
            # Check that the necessary environment variables are set    
            request = sys.argv[1]
            
            # Validate the user input
            if not request:
                raise ValueError("No input provided. Please provide a message.")
            
            print("Current prompt: ", request, "\n")

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

            # Initialize the client
            client = openai.OpenAI()

            # Step 1: Create an Assistant
            assistant = client.beta.assistants.create(
                name="Fire And Forget Assistant",
                instructions=instructions,
                tools=tools_list,
                model=OPENAI_MODEL,
            )

            # Step 2: Create a Thread
            thread = client.beta.threads.create()

            # Step 3: Add a Message to a Thread
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=request
            )

            # Step 4: Run the Assistant
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
            while True:
                # Wait for 5 seconds
                time.sleep(5)

                # Retrieve the run status
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

                # If run is completed, get messages
                if run_status.status == 'completed':
                    messages = client.beta.threads.messages.list(
                        thread_id=thread.id
                    )

                    print("Final output:")
                    print(faf_output)

                    # Loop through messages in reverse order and print content based on role
                    for msg in reversed(messages.data):
                        role = msg.role
                        content = msg.content[0].text.value
                        print(f"{role.capitalize()}: {content}")

                    break
                elif run_status.status == 'requires_action':

                    print("Function Calling")
                    required_actions = run_status.required_action.submit_tool_outputs.model_dump()
                    print(required_actions)

                    tool_outputs = [call_tool_function(action) for action in required_actions["tool_calls"]]
                    faf_output = tool_outputs[0]["output"]

                    print("Submitting outputs back to the Assistant...")
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                else:
                    print("Waiting for the Assistant to process...")
                    time.sleep(5)

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


    if faf_output:
        write_to_file(faf_output)
        
if __name__ == "__main__":
    main()
    
    