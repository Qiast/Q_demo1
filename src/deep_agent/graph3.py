from typing import Dict, Any, List
from langchain_core.messages import ToolMessage, AIMessage
import asyncio
import json
from langchain_mcp_adapters.client import MultiServerMCPClient

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

class BasicToolNode:
    """
    异步工具节点,用于并发执行AIMessage中请求的工具调用

    功能:
    1. 接收工具列表并建立名称索引
    2. 并发执行消息中的工具调用请求
    3. 自动处理同步/异步工具适配
    """
    def __init__(self, tools: list):
        """
        初始化工具节点
        Args:
            tools:工具列表,每个工具需包含name属性
        """
        self.tools_by_name = {tool.name for tool in tools}

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, List[ToolMessage]]:
        """
        异步调用入口
        Args:
            inputs:输入字典,需包含"messages"字段
        Returns:
            包含ToolMessage列表的字典
        Raises:
            ValueError:当输入无效时抛出
        """
        # 输入验证
        if not (messages := state.get("messages")):
            raise ValueError("Invalid input")
        message: AIMessage = messages[-1]

        # 并发执行工具调用
        outputs = await self._execute_tool_calls(message.tool_calls)
        return {"messages": outputs}

    async def _execute_tool_calls(self, tool_calls: List[Dict]) -> List[ToolMessage]:
        """
        执行实际工具时调用
        Args:
            tool_calls:工具调用请求列表
        Returns:
            ToolMessage结果列表
        """

        async def _invoke_tool(tool_call: Dict) -> ToolMessage:
            """执行单个工具时调用
            Args:
                tool_call:工具调用请求字典,需包含name/args/id字段
            Returns:
                封装的ToolMessage
            Raises:
                KeyError:工具未注册时抛出
                RuntimeError:工具调用失败时抛出
            """
            try:
                # 异步调用工具
                tool = self.tools_by_name.get(tool_call["name"])
                if not tool:
                    raise KeyError(f"tool: {tool_call['name']} not registered")

                if hasattr(tool, 'ainvoke'):
                    # 优先异步调用
                    tool_result = await tool.ainvoke(tool_call["args"])
                else: #转化为异步调用
                    loop = asyncio.get_running_loop()
                    tool_result = await loop.run_in_executor(
                        None,
                        tool.ainvoke,
                        tool_call["args"]
                    )

                return ToolMessage(
                    content = json.dumps(tool_result, ensure_ascii = False),
                    name = tool_call["name"],
                    tool_call_id = tool_call["id"]
                )
            except Exception as e:
                raise RuntimeError(f"tool: {tool_call['name']} invoke failed: {e}")

        try:
            # 5. 并发执行所有工具调用
            # ''1

            # asyncio.gather()是 Python 异步编程中用于并发调度多个协程的核心函数,其核心行为包括:
            # 并发执行:所有传入的协程会被同时调度到事件循环中,通过非阻塞 I/0 实现并行处理。
            # 结果收集:按输入顺序返回所有协程的结果(或异常),与任务完成顺序无关。
            # 异常处理:默认情况下,任一任务失败会立即取消其他任务并抛出异常;若设置 return_exceptions=True,则异常会作为结果
            return await asyncio.gather( *[_invoke_tool(tool_call) for tool_call in tool_calls])
        except Exception as e:
            raise RuntimeError("failed") from e