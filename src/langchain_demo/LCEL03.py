from langchain_core.prompts import ChatPromptTemplate
from deep_agent.graph3_copy_interrupt import llm

gather_preference_prompt = ChatPromptTemplate.from_template(
    "用户输入了一些餐厅偏好：{input1}\n"
    "请将用户偏好总结为清晰的需求"
)

recommend_restaurant_prompt = ChatPromptTemplate.from_template(
    "基于用户需求：{input2}\n"
    "请推荐3个合适的餐厅并说明理由"
)

summarize_recommendations_prompt = ChatPromptTemplate.from_template(
    "以下是餐厅推荐和推荐理由:\n{input3}\n"
    "请总结成 2-3 句话,供用户快速参考:"
)