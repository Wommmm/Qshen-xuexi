from mcp.client.stdio import stdio_client
from mcp import ClientSession,StdioServerParameters
# 利用client端调用server端，重难点为以下，配置命令行参数
# server_params = StdioServerParameters(
#         command=r"d:\LANGCHANINDEMO\.venv\Scripts\python.exe",
#         args=[r"D:\LANGCHANINDEMO\september\Day04\mcp_stdio_server.py"],
#     )
#创建客户端，需要异步连接 async
async def main():
    server_params = StdioServerParameters(
        command=r"d:\LANGCHANINDEMO\.venv\Scripts\python.exe",
        args=[r"D:\LANGCHANINDEMO\september\Day04\mcp_stdio_server.py"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(
            read_stream=read_stream,
            write_stream=write_stream,
        ) as session :
            await session.initialize()

            tools_list = await session.list_tools()
            #调用server中的工具
            result = await session.call_tool("get_weather",{"city":"上海", "date":"2023-09-01"})


            print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
