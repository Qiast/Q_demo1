import asyncio
from langgraph_sdk import get_client

client = get_client(url = "http://localhost:2024")

async def main():
    async for chunk in client.runs.stream(
        None,
        assistant_id = "agent",
        input = {
            "messages": [
                {
                    "role": "human",
                    "content": "How old am I this year?"
                }
            ]
        },
        config = {"configurable": {"user_name": "Qiast.Fy"}},
        stream_mode = "messages-tuple"  #流式输出
    ):
        # print(chunk.data)
        # print("\n\n")
        if isinstance(chunk.data, list) and 'type' in chunk.data[0] and chunk.data[0]['type'] == 'AIMessageChunk':
            print(chunk.data[0]['content'], end = "", flush = True)

if __name__ == "__main__":
    asyncio.run(main())