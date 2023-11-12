import sys

import time
import openai
import json

from helpers import get_env_var, validate_user_input
from tools import follow_up_then, user_note, save_url

tools_list = [{
    "type": "function",
    "function": {
        "name": "follow_up_then",
        "description": """Send a follow-up reminder with the given date and message. Use only if there is a specific date provided or some time reference like "tomorrow" or "in 2 days".
Additional contraits for the date:

- Do not use "this" in the date like "thisMonday" or "thisTuesday" as FUT does not support them.
- Do not user "in a week", "in two weeks" or "in a month" replace them with "1week",  "2weeks" and "1month" respectively. 
- Date cannot have any spaces, dots or commas.""",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date of the follow-up in the format like '1August', 'tomorrow3pm' or 'in2days'."
                },
                "message": {
                    "type": "string",
                    "description": "Message to send."
                }
            },
            "required": ["date", "message"]
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
                "message": {
                    "type": "string",
                    "description": "Message to send."
                }
            },
            "required": ["message"]
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
                "url": {
                    "type": "string",
                    "description": "URL to append to the URL list."
                }
            },
            "required": ["url"]
        }
    }
}
]

if __name__ == "__main__":
    
    try:
        # Check that the necessary environment variables are set
        #openai_key = get_env_var('OPENAI_API_KEY')
        
        request = sys.argv[1]
        validate_user_input(request)
        print("Current prompt: ", request, "\n")

        # Initialize the client
        client = openai.OpenAI()

        # Step 1: Create an Assistant
        assistant = client.beta.assistants.create(
            name="Fire And Forget Assistant",
            instructions="You are a personal assistant, helping the user to manage their schedule. You use various tools to process follow ups, set reminders, collect URLs and schedule calendar events. Note that the user will sometimes talk as if they were giving instructions to you, but in fact they want you to send these instructions to them, either as reminders or follow ups etc. Never replace user input with URLs or other links.",
            tools=tools_list,
            model="gpt-4-1106-preview",
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
                tool_outputs = []

                for action in required_actions["tool_calls"]:
                    func_name = action['function']['name']
                    arguments = json.loads(action['function']['arguments'])
                    
                    if func_name == "follow_up_then":
                        print("Calling follow_up_then with arguments: ", arguments)
                        output = follow_up_then(date=arguments['date'], message=arguments['message'])
                        tool_outputs.append({
                            "tool_call_id": action['id'],
                            "output": output
                        })
                    elif func_name == "user_note":
                        print("Calling user_note with arguments: ", arguments)
                        output = user_note(message=arguments['message'])
                        tool_outputs.append({
                            "tool_call_id": action['id'],
                            "output": output
                        })
                    elif func_name == "save_url":
                        print("Calling save_url with arguments: ", arguments)
                        output = save_url(url=arguments['url'])
                        tool_outputs.append({
                            "tool_call_id": action['id'],
                            "output": output
                        })
                    else:
                        raise ValueError(f"Unknown function: {func_name}")
                    
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




exit()
# Define prefix and suffix for creating prompts
prefix = """Answer the following questions as best you can.
Note that the user will sometimes talk as if they were giving instructions to you, but in fact they want you 
to send these instructions to them, either as reminders or follow ups. Never replace user input with URLs or
other links. Always use the tools provided below to process the input.
You have access to the following tools, but you are only allowed to use one of them:"""
suffix = """Begin! Remember - you only need to use one tool and always act with a tool in your first action.
If you don't know what to do, pass the user note to Self Note tool, without any modification.
Never ask for clarification.

User wants to you to process the following input using only the tools above, in a single step. Choose the best tool for it: {input}
{agent_scratchpad} """

fut = StructuredTool.from_function(follow_up_then, name="Follow Up Then")
note = StructuredTool.from_function(user_note, name="Note to Self")
url = StructuredTool.from_function(save_url, name="Save URL")

tools = [note, fut, url]

tool_names = [tool.name for tool in tools]

prompt = StructuredChatAgent.create_prompt(
    tools, prefix=prefix, suffix=suffix, input_variables=["input", "agent_scratchpad"]
)
llm_chain = LLMChain(llm=ChatOpenAI(temperature=0, model="gpt-4"), prompt=prompt)

# Create a StructuredChatAgent and an AgentExecutor for running the agent with our tools
agent = StructuredChatAgent(llm_chain=llm_chain, allowed_tools=tool_names)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True, 
)

agent_executor.max_iterations=1

if __name__ == "__main__":
    
    try:
        # Check that the necessary environment variables are set
        openai_key = get_env_var('OPENAI_API_KEY')
        
        msg = sys.argv[1]
        validate_user_input(msg)
        print("Current prompt: \n", msg, "\n")
        agent_executor.run(msg)
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
