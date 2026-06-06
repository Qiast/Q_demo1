from typing import Annotated
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from deep_agent.my_state import CustomState


@tool
def get_user_info(config: RunnableConfig) -> dict:
    """Getting user's information including name, sex and so on."""
    user_name = config['configurable'].get('user_name', 'Qiast')
    print(f"name is {user_name}")
    return {'username': user_name, 'sex': 'male', 'age': 193}

@tool
def revise_user_info(tool_call_id: Annotated[str, InjectedToolCallId], config: RunnableConfig) -> Command:
    """Getting user's information including name, sex and so on."""
    user_name = config['configurable'].get('user_name', 'Qiast')
    print(f"name is {user_name}")
    return Command(update = {
        "username": user_name,
        "messages": [
            ToolMessage(
                content = 'The information has been successfully modified.',
                tool_call_id = tool_call_id
            )
        ]
    })


@tool
def greet_user(state: Annotated[CustomState, InjectedState]):
    """Greeting username and generating congratulation"""
    username = state['username']
    return f"Congratulation,{username}!"