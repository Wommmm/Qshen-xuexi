from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession

async def main():
    Url = "http://127.0.0.1:8000/mcp"

    async with streamable_http_client(url=Url) as (read_stream, write_stream,_):
        async with ClientSession(
            read_stream=read_stream,
             write_stream=write_stream
            ) as session:
            # 初始化
            await session.initialize()

            tools_list = await session.list_tools()

            print(tools_list)

            # 调用
            result = await session.call_tool(name="get_weather", arguments={"city": "广西", "date": "2023-09-01"})

            print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())            