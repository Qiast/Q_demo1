from typing import TypedDict, Literal
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from .graph import llm
from langgraph.graph import StateGraph
from langgraph.constants import END, START

class State(TypedDict):
    joke: str
    topic: str
    feedback: str
    funny_or_not: str

def generate_joke(state: State):
    """Generate a joke using an llm"""
    prompt = (
        f"improve the joke based on feedback: {state['feedback']}\n topic: {state['topic']}"
        if state.get("feedback", None)
        else f"generate a joke about {state['topic']}"
    )

    # resp = llm.invoke(prompt)
    chain = llm | StrOutputParser()
    resp = chain.invoke(prompt)
    return {"joke": resp}

class Feedback(BaseModel):
    """使用此工具来结构化响应"""
    grade: Literal["funny", "not funny"] = Field(
        description = "judging whether a joke is funny",
        examples = ["funny", "not funny"]
    )
    feedback: str = Field(
        description = "If it's not humorous, offer suggestions for improvement",
        examples = "You can add puns."
    )

def evaluate_joke(state: State):
    """Evaluating joke from State"""
    chain = llm.with_structured_output(Feedback)
    resp = chain.invoke(
        f'evaluate the humor level of the joke: \n{state['joke']}\n'
        'Note: Humor should involve element of surprise or clever phrasing'
    )

    return {
        'feedback': resp.feedback,
        'funny_or_not': resp.grade
    }

def route_function(state: State):
    """动态路由决策函数"""
    return 'Ye' if state['funny_or_not'] == 'funny' else "Noo"

builer = StateGraph(State)

builer.add_node("generator", generate_joke)
builer.add_node("evaluator", evaluate_joke)

builer.add_edge(START, "generator")
builer.add_edge("generator", "evaluator")
builer.add_conditional_edges(
    "evaluator",
    route_function,
    {
        "Ye": END,
        "Noo": "generator"
    }
)

joke_graph = builer.compile()