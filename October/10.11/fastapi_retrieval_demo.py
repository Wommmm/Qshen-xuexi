from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
import os

app = FastAPI()

DOCUMENTS = [
    {
        "id": "doc-1",
        "content": "FastAPI 用于构建 HTTP API",
        "source": "fastapi-docs",
    },
    {
        "id": "doc-2",
        "content": "FastAPI 使用 Pydantic 校验请求参数",
        "source": "fastapi-docs",
    },
    {
        "id": "doc-3",
        "content": "LangGraph Agent 可以通过 FastAPI 接口提供服务",
        "source": "langgraph-docs",
    },
    {
        "id": "doc-4",
        "content": "LangChain 可以将 Python 函数包装成工具",
        "source": "langchain-docs",
    },
]


# BaseModel是Pydantic的基类：声明输入字段，供接口和工具共同校验参数。
class RetrievalRequest(BaseModel):
  # Field设置校验规则；min_length限制长度，不会自动去掉空格。
  query: str = Field(min_length=1)
  # default设置默认值；ge/le分别表示大于等于/小于等于。
  top_k: int = Field(default=3,ge=1,le=10)
  source: str | None =None


class RetrievalService():
  def __init__(self,documents:list[dict]):
    self.documents = documents

  def retrieve(self,query:str,top_k:int,source: str | None = None,) -> list[dict]:
    if query == "模拟故障":
      raise RuntimeError("服务不可用")
    keyword = query.strip().lower()
    if not keyword:
      return []
    results = []
    for doc in self.documents:
      if source is not None and doc["source"] != source:
        continue

      if keyword in doc["content"].lower():
        results.append(doc)

    return results[:top_k]    


service = RetrievalService(DOCUMENTS)
# tool是LangChain的装饰器：把下方函数包装成工具对象。
# args_schema传入参数模型类，复用query/top_k/source的字段与校验规则。
@tool(args_schema = RetrievalRequest)
def search_documents(
  query: str,
  top_k: int = 3,
  source: str | None = None,
):
  """
  按关键词搜索本地资料，可按来源过滤并限制返回数量。
  """
  # 工具包装负责接收参数，Service仍然负责真正的检索业务。
  documents = service.retrieve(query=query,top_k=top_k,source=source)
  return {"documents":documents,"count":len(documents)}


def get_retrieval_service():
  return service

@app.post("/retrieve")
async def retrieve(request: RetrievalRequest,retrieval_service:RetrievalService=Depends(get_retrieval_service)):
  try:
    documents = retrieval_service.retrieve(
      query = request.query,
      top_k = request.top_k,
      source=request.source,
    )
    return {"documents":documents,"count":len(documents)}
  except RuntimeError as e:
    raise HTTPException(status_code=503, detail=str(e))
  

if __name__ == "__main__":
    api_key = os.getenv("new_apikey")
    if not api_key:
        raise RuntimeError("请设置环境变量new_apikey")

    model = ChatOpenAI(
      model = "qwen-plus",
      api_key = api_key,
      base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
      timeout=60,
      max_retries=0,
    )
    # 提供工具说明和参数结构，由模型按需选择是否调用工具。
    model_with_tools = model.bind_tools([search_documents],tool_choice="auto")
    question = (
  "检索本地资料中有关langchain的内容"
  "检索关键词使用langchain，并解释他的作用"
    )
    ## messages是普通Python列表，按对话发生的顺序保存消息。
    # HumanMessage把用户问题标记为“用户输入”。
    messages = [HumanMessage(content=question)]
    model_reply = model_with_tools.invoke(messages)
    messages.append(model_reply)
    print("模型提出的工具请求：", model_reply.tool_calls)
    # 空列表表示模型没有请求调用工具。
    if not model_reply.tool_calls:
      print("直接回答：",model_reply.content)
    else:
      #有model_reply.tool_calls,执行工具，并且加入消息历史。
      for tool_call in model_reply.tool_calls:
        tool_reply = search_documents.invoke(tool_call)
        messages.append(tool_reply)
        print("工具返回：",tool_reply.content)

      # 仅在工具执行后请求模型总结；不再提供工具，直接生成回答。
      final_reply = model.invoke(messages)
      print("最终回答：",final_reply.content)
    



