from mcp.server.fastmcp import FastMCP
from fastapi_retrieval_demo import search_documents

mcp = FastMCP(
    "本地文档检索",
    host="127.0.0.1", port=8051,
    streamable_http_path="/mcp/",
)

@mcp.tool(name = "search_documents")#server暴露的工具名称
#retrieve_documents：本地 Python 函数名
def retrieve_documents(
    query: str,
    top_k: int = 3,
    source: str | None = None,
    min_content_length:int=0,
) -> dict[str,object]:
    # "search_documents"：客户端调用时使用的工具名
    return search_documents.invoke({
        "query": query,
        "top_k": top_k,
        "source": source,
        "min_content_length":min_content_length,
    })

if __name__ == "__main__":
    mcp.run(transport="streamable-http")