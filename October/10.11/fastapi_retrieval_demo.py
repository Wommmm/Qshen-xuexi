from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
import json
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


class AnswerResult(BaseModel):
    # 类型和min_length用于校验。
    # description描述字段用途，也会作为提示提供给模型。
    answer:str = Field(
      min_length=1,
      description="最终回答；资料问答只使用检索正文支持的信息",
    )

    sources: list[str] = Field(
      description =(
          "来源列表，取自本次检索文档的source字段；"
          "未检索或没有匹配资料时返回空列表"
      ),
    )
    
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

def find_invalid_Soruces(
    messages:list,
    claimed_sources:list[str],
)-> list[str]:
  """返回模型声明中、不属于本次检索结果的来源。"""  
  allowed_sources = set()
  invalid_sources = []
  for message in messages:
    if message.type == "tool"and message.name == "search_documents":
      data = json.loads(message.content)
      for doc in data["documents"]:
        allowed_sources.add(doc["source"])
  for source in claimed_sources:
    if source not in allowed_sources:
      invalid_sources.append(source)
  return invalid_sources    
         

      

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
    agnet = create_agent(
      model = model,
      tools=[search_documents],
      system_prompt=("你是一个技术资料助手。"
            "涉及本地资料的问题，先使用检索工具。"
            "普通问候或简单计算可以直接回答。"
            "依据检索资料回答时说明来源；"
            "资料没有支持的内容，不要编造。"
            "如果检索结果为空，明确说明没有找到本地资料。"
            "不要重复执行相同参数的检索。"
      ),
        # 按AnswerResult组织答案，并由框架解析、校验。
      response_format=ToolStrategy(AnswerResult),
    )
    question =[
         "什么是agent", 


        "请检索FastAPI，来源限定为langgraph-docs，"
        "最多返回两条，并依据本地资料解释它与LangGraph的关系。",


        "请使用Docker作为关键词检索本地资料，"
        "如果没有匹配资料，请明确说明。",
    ]
    for q in question:
     print("\n问题：",q)
  
     result = agnet.invoke({"messages":[HumanMessage(content=q)]},config = {"recursion_limit":10})

     roles = [message.type for message in result["messages"]]
     print("信息角色顺序",roles)

     for message in result["messages"]:
       if(
         message.type == "tool" and
         message.name == "search_documents"
       ):
         print("检索结果",message.content)

     strucured = result["structured_response"]  

     print("回答：", strucured.answer)
     print("来源：", strucured.sources)

     # model_dump是Pydantic方法，将模型对象转换为字典。
     print("完整结果：", strucured.model_dump())


      
