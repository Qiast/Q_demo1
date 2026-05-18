# """Deep Agent graph for deployment."""
#
# from __future__ import annotations
#
# import contextlib
# import os
# from datetime import datetime, timezone
#
# from langchain_core.runnables import RunnableConfig
#
# from deepagents import create_deep_agent
# from langchain_core.tools import tool
# from langgraph_sdk.runtime import ServerRuntime
#
# from deep_agent.sandbox import get_or_create_sandbox
#
# DEFAULT_MODEL = os.getenv("DEEP_AGENT_MODEL", "anthropic:claude-sonnet-4-6")
#
# SYSTEM_PROMPT = """
# You are a deep agent.
#
# Workflow:
# 1. Write and maintain a todo list for non-trivial requests.
# 2. Delegate focused fact-finding to subagents when helpful.
# 3. Store intermediate drafts in files when the task is long.
# 4. Before finalizing, critique your work for risks, gaps, and missing constraints.
# 5. Return concise, actionable output.
#
# - Prefer concrete evidence over assumptions.
# - State unresolved uncertainty explicitly.
# - Keep output compact unless the user asks for depth.
# """.strip()
#
#
# @tool
# def utc_now() -> str:
#     """Return the current UTC timestamp in ISO format."""
#     return datetime.now(tz=timezone.utc).isoformat()
#
#
# SUBAGENTS = [
#     {
#         "name": "researcher",
#         "description": "Use for evidence collection and source-grounded fact finding.",
#         "system_prompt": (
#             "You are a focused researcher. Gather evidence, list assumptions, and "
#             "report contradictions clearly."
#         ),
#         "tools": [utc_now],
#     },
#     {
#         "name": "critic",
#         "description": "Use for adversarial review of drafts and plans.",
#         "system_prompt": (
#             "You are a critical reviewer. Find weak logic, untested assumptions, and "
#             "missing constraints."
#         ),
#         "tools": [utc_now],
#     },
# ]
#
#
# def _build_agent(backend=None):
#     return create_deep_agent(
#         model=DEFAULT_MODEL,
#         tools=[utc_now],
#         backend=backend,
#         system_prompt=SYSTEM_PROMPT,
#         subagents=SUBAGENTS,
#         # You can disable these if you want to run without interrupts
#         interrupt_on={
#             "execute": True, "write_file": True},
#         name="deep_agent",
#     )
#
#
# RO_AGENT = _build_agent()
#
#
# @contextlib.asynccontextmanager
# async def get_agent(config: RunnableConfig, runtime: ServerRuntime):
#     ert = runtime.execution_runtime
#     if ert:
#         thread_id = config.get("configurable", {}).get("thread_id", "default")
#         backend = await get_or_create_sandbox(thread_id)
#         yield _build_agent(backend=backend)
#     else:
#         yield RO_AGENT
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
# from deep_agent.tools.tools_three import get_asset
from langchain_core.messages import AnyMessage

from deep_agent.my_state import CustomState
from deep_agent.tools.tools_four import get_user_info, greet_user

# checkpointer = InMemorySaver

# 使用configurable生成系统提示词
def system_prompt(state: AgentState, config: RunnableConfig) ->  list[AnyMessage]:
    user_name = config['configurable'].get('user_name', 'Qiast')
    system_message = (f'you are a helpful assistant, your master name is {user_name}')
    return [{'role': 'system', 'content': system_message}] + state['messages']

llm = ChatOllama(
    model = "qwen3.5:4b",
    temperature = 0.3,
)

def get_weather(city: str) -> str:
    """Get the weather in a given city."""
    return f"It's always sunny in {city}!"

graph = create_react_agent(
    llm,
    tools = [get_weather, get_user_info, greet_user],
    prompt = system_prompt,
    state_schema = CustomState
    # checkpoint = checkpoint
)