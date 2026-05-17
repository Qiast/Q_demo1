from langgraph.prebuilt.chat_agent_executor import AgentState


class CustomState(AgentState):
    username: str