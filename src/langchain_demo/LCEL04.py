from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RouterRunnable

from deep_agent.graph3_copy_interrupt import llm

# 定义数学任务模板
math_template = ChatPromptTemplate. from_template(
    "你是一位数学家,擅长分步骤解决数学问题,并提供详细的解决过程。以下是问题内容:{input}"
)

# 定义历史任务模板
history_template = ChatPromptTemplate. from_template(
    "你是一位历史学家,对历史事件和背景有深入研究。以下是问题内容:{input}"
)

# 定义物理任务模板
physics_template = ChatPromptTemplate. from_template(
    "你是一位物理学教授,擅长用简洁易懂的方式回答物理问题。以下是问题内容:{input}"
)

default_template = ChatPromptTemplate. from_template(
    "你是一位智能助手,能够处理各种问题。以下是"
    "问题内容:{input}"
)

default_chain = default_template | llm
math_chain = math_template | llm
history_chain = history_template | llm
physics_chain = physics_template | llm

def route_chain(input):
    if '物理' in input['type']:
        print("物理")
        return {"key": 'physics', "input": input['input']}
    elif '历史' in input['type']:
        print("历史")
        return {"key": 'history', "input": input['input']}
    elif '数学' in input['type']:
        print("数学")
        return {"key": 'math', "input": input['input']}
    return {"key": 'default', "input": input['input']}

route_func = RunnableLambda(route_chain)

# 路由调度器
router = RouterRunnable(runnables = {
    'physics': physics_chain,
    'history': history_chain,
    'math': math_chain,
    'default': default_chain
})

# 第一个提示词模板:
first_temp = ChatPromptTemplate. from_template(
    "不要回答下面用户的问题,只要根据用户的输入来判断分类,一共有[物理,历史,计算机,数学,其他]5种类别。\n\n \
    用户的输入:{input} \n\n \
    最后的输出包含分类的类别和用户输入的内容,输出格式为json.其中,类别的key为type,用户输入内容的key为input"
)

chain = first_temp | llm | JsonOutputParser() | route_func | router | StrOutputParser()

inputs = [
    {"input": "物理是什么?"},
    {"input": "历史是什么?"},
    {"input": "数学是什么?"},
    {"input": "计算机是什么?"}
]

for content in inputs:
    result = chain.invoke(content)
    print(f'q: {content["input"]}, a: {result}')