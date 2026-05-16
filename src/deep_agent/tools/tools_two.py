# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import PromptTemplate
# from pydantic import BaseModel, Field
#
# from deep_agent.graph import llm
#
# # 根据runnable对象创建tool
# # 把chain转化为tool
#
# prompt = (
#     PromptTemplate.from_template(
#         "Please generate a short introduction for {topic}."
#     ) + "The output content is in {language}."
# )
#
# chain = prompt | llm | StrOutputParser()
#
# class ToolArgs(BaseModel):
#     topic: str = Field(description = "The topic of the introduction.")
#     language: str = Field(description = "The language of the introduction.")
#
# runnable_tool = chain.as_tool(
#     name = 'chain_tool',
#     description = "This is a tool for generating introduction.",
#     args_schema = ToolArgs,
# )