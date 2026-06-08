from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

from deep_agent.graph3_copy_interrupt import llm

prompt1 = PromptTemplate.form_template('给我写一篇关于{key_word}的{type},字数不超过{count}。')
prompt2 = PromptTemplate.form_template('请简单评价一下这篇短文,如果总分是10分,请给这篇短文打分:{text_content}')

chain1 = prompt1 | llm | StrOutputParser()
# chain = {'text_content': prompt1 | llm | StrOutputParser()} | prompt2 | llm | StrOutputParser()

def print_func(input):
    print(input)
    print('=' * 20)
    return {'text_content': input}

# 可以显示文本
chain = prompt1 | llm | StrOutputParser() | RunnableLambda(print_func) | prompt2 | llm | StrOutputParser()
