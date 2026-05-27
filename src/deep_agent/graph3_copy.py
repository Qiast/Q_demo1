import os
from dotenv import load_dotenv
from typing import Dict, Any, List
from langchain_core.messages import ToolMessage, AIMessage
import asyncio
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph
from langgraph.constants import END, START
from langgraph.prebuilt import ToolNode, tools_condition

my12306_mcp_server_config = {
    'url': 'https://mcp.api-inference.modelscope.net/f8f7367c4e4444/mcp',
    'transport': 'streamable_http'
}

chart_mcp_server_config = {
    'url': 'https://mcp.api-inference.modelscope.net/49e1806755a142/sse',
    'transport': 'sse'
}

mcp_client = MultiServerMCPClient(
    {
        'chart_mcp': chart_mcp_server_config,
        '12306_mcp': my12306_mcp_server_config
    }
)

load_dotenv()

llm = ChatOpenAI(
    model = "deepseek-v4-flash",
    temperature = 0.7,
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = "https://api.deepseek.com"
)

# class BasicToolNode:
#     """
#     异步工具节点,用于并发执行AIMessage中请求的工具调用
#
#     功能:
#     1. 接收工具列表并建立名称索引
#     2. 并发执行消息中的工具调用请求
#     3. 自动处理同步/异步工具适配
#     """
#     def __init__(self, tools: list):
#         """
#         初始化工具节点
#         Args:
#             tools:工具列表,每个工具需包含name属性
#         """
#         self.tools_by_name = {tool.name for tool in tools}
#
#     async def __call__(self, state: Dict[str, Any]) -> Dict[str, List[ToolMessage]]:
#         """
#         异步调用入口
#         Args:
#             inputs:输入字典,需包含"messages"字段
#         Returns:
#             包含ToolMessage列表的字典
#         Raises:
#             ValueError:当输入无效时抛出
#         """
#         # 输入验证
#         if not (messages := state.get("messages")):
#             raise ValueError("Invalid input")
#         message: AIMessage = messages[-1]
#
#         # 并发执行工具调用
#         outputs = await self._execute_tool_calls(message.tool_calls)
#         return {"messages": outputs}
#
#     async def _execute_tool_calls(self, tool_calls: List[Dict]) -> List[ToolMessage]:
#         """
#         执行实际工具时调用
#         Args:
#             tool_calls:工具调用请求列表
#         Returns:
#             ToolMessage结果列表
#         """
#
#         async def _invoke_tool(tool_call: Dict) -> ToolMessage:
#             """执行单个工具时调用
#             Args:
#                 tool_call:工具调用请求字典,需包含name/args/id字段
#             Returns:
#                 封装的ToolMessage
#             Raises:
#                 KeyError:工具未注册时抛出
#                 RuntimeError:工具调用失败时抛出
#             """
#             try:
#                 # 异步调用工具
#                 tool = self.tools_by_name.get(tool_call["name"])
#                 if not tool:
#                     raise KeyError(f"tool: {tool_call['name']} not registered")
#
#                 if hasattr(tool, 'ainvoke'):
#                     # 优先异步调用
#                     tool_result = await tool.ainvoke(tool_call["args"])
#                 else: #转化为异步调用
#                     loop = asyncio.get_running_loop()
#                     tool_result = await loop.run_in_executor(
#                         None,
#                         tool.ainvoke,
#                         tool_call["args"]
#                     )
#
#                 return ToolMessage(
#                     content = json.dumps(tool_result, ensure_ascii = False),
#                     name = tool_call["name"],
#                     tool_call_id = tool_call["id"]
#                 )
#             except Exception as e:
#                 raise RuntimeError(f"tool: {tool_call['name']} invoke failed: {e}")
#
#         try:
#             # 5. 并发执行所有工具调用
#             # ''1
#
#             # asyncio.gather()是 Python 异步编程中用于并发调度多个协程的核心函数,其核心行为包括:
#             # 并发执行:所有传入的协程会被同时调度到事件循环中,通过非阻塞 I/0 实现并行处理。
#             # 结果收集:按输入顺序返回所有协程的结果(或异常),与任务完成顺序无关。
#             # 异常处理:默认情况下,任一任务失败会立即取消其他任务并抛出异常;若设置 return_exceptions=True,则异常会作为结果
#             return await asyncio.gather( *[_invoke_tool(tool_call) for tool_call in tool_calls])
#         except Exception as e:
#             raise RuntimeError("failed") from e

class State(MessagesState):
    pass

# def route_tools_function(state: State):
#     """动态路由函数,如果从大模型输出后的AIMessage,中包含有工具调用的请求(指令),就进入到tools节点,否则则结束"""
#     if isinstance(state, list):
#         ai_message = state[-1]
#     elif messages := state.get['message']:
#         ai_message = messages[-1]
#     else:
#         raise ValueError("Invalid input")
#     if hasattr(ai_message, 'tool_calls') and len(ai_message.tool_calls) > 0:
#         return "tools"
#     return END

async def create_graph():
    tools = await mcp_client.get_tools()
    builder = StateGraph(State)
    llm_with_tools = llm.bind_tools()

    async def chatbot(state: State):
        return {"messages": [await llm_with_tools.ainvoke(state["messages"])]}

    # tool_node = BasicToolNode(tools)
    tool_node = ToolNode(tools)

    builder.add_node('chatbot', chatbot)
    builder.add_node('tools', tool_node)
    builder.add_conditional_edges(
        "chatbot",
        tools_condition
    )
    builder.add_edge(START, "chatbot")
    builder.add_edge("tools", "chatbot")
    # 设置检查点
    memory = MemorySaver()
    return builder.compile(checkpointer = memory, interrupt_before = ['tools'])  #加入人工干预

# agent = asyncio.run(create_graph())


async def run_agent():
    graph = await create_graph()
    config = {
        "configurable": {
            "thread_id": 'red123'
        }
    }

    def print_message(event, result):
        """格式化输出消息"""
        messages = event.get("messages")
        if messages:
            if isinstance(messages, list):
                message = messages[-1]
            if message.__class__.__name__ == 'AIMessage':
                if message.content:
                    result = message.content
            msg_repr = message.pretty_repr(html = True)
            if len(msg_repr) > 1500:
                msg_repr = msg_repr[:1500] + "..."
            print(msg_repr)
        return result

    def get_answer(tool_message, user_answer):
        """由人工介入，并且给问题一个答案"""
        tool_name = tool_message.tool_calls[0]['name']
        answer = (
            f"人工强制终止了工具:{tool_name}的执行,拒绝的理由是:{user_answer}"
        )
        new_message = [
            ToolMessage(content = answer, tool_call_id = tool_message.tool_calls[0]['id']),
            AIMessage(content = answer)
        ]

        # 人工信息添加到state中
        graph.update_state(
            config = config,
            values = {'message': new_message}
        )

    async def execute_graph(user_input: str) -> str:
        """执行工作流的函数"""
        result = ""
        if user_input.strip().lower() != "y":
            current_state = graph.get_state(config)
            if current_state.next:
                tools_script_message = current_state.values['message'][-1]
                get_answer(tools_script_message, user_input)
                message = graph.get_state(config).values['message'][-1]
                result = message.content
                return result
            else:
                async for chunk in graph.astream({'messages': ('user', user_input)}, config, stream_mode = 'values'):
                    result = print_message(chunk, result)
        else:
            async for chunk in graph.astream(None, config, stream_mode = 'values'):
                result = print_message(chunk, result)

        current_state = graph.get_state(config)
        if current_state.next:   #出现工作流中断
            ai_message = current_state.values['message'][-1]
            tool_name = ai_message.tool_calls[0]['name']
            result = f"AI助手马上根据你的要求，执行{tool_name}工具。你是否批准继续执行？输入'y'继续，否则说明理由。"

        return result

    while True:
        user_input = input("user: ")
        res = await execute_graph(user_input)
        print('AI:', res)

if __name__ == '__main__':
    asyncio.run(run_agent())