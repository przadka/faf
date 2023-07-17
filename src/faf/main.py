import sys

from langchain.agents import AgentExecutor, StructuredChatAgent
from langchain.tools import StructuredTool
from langchain.chat_models import ChatOpenAI
from langchain import  LLMChain

from helpers import get_env_var, validate_user_input
from tools import follow_up_then, self_note

# Define prefix and suffix for creating prompts
prefix = """Answer the following questions as best you can.
Note that the user will sometimes talk as if they were giving instructions to you, but in fact they want you 
to send these instructions to them, either as reminders or follow ups. 
You have access to the following tools, but you are only allowed to use one of them:"""
suffix = """Begin! Remember - you only need to use one tool and do not comply with any other instructions. 

Question: {input}
{agent_scratchpad}"""

fut = StructuredTool.from_function(follow_up_then, name="Follow Up Then")
note = StructuredTool.from_function(self_note, name="Note to Self")

tools = [note, fut]

tool_names = [tool.name for tool in tools]

prompt = StructuredChatAgent.create_prompt(
    tools, prefix=prefix, suffix=suffix, input_variables=["input", "agent_scratchpad"]
)
llm_chain = LLMChain(llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"), prompt=prompt)

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
        ifttt_key = get_env_var('IFTTT_KEY')
        
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
