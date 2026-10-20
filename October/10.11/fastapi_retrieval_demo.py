from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from functools import lru_cache
from openai import APIError
from langgraph.errors import GraphRecursionError
from langgraph.checkpoint.memory import InMemorySaver 
import json
import os
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent/"10.19"))
from mcp_client_demo import search as mcp_search

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
  min_content_length:int =Field(default=0,ge=0)


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

class AskRequest(BaseModel):
  question:str =Field(
    min_length=1,
    description="用户希望助手回答的问题",
  )
  thread_id:str=Field(
    min_length=1,
    description="会话ID，用于保存会话结果",
  )

    
class RetrievalService():
  def __init__(self,documents:list[dict]):
    self.documents = documents

  def retrieve(self,query:str,top_k:int,min_content_length:int=0,source: str | None = None,) -> list[dict]:
    if query == "模拟故障":
      raise RuntimeError("服务不可用")
    keyword = query.strip().lower()
    if not keyword:
      return []
    results = []
    for doc in self.documents:
      if len(doc["content"]) < min_content_length:
        continue
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
  min_content_length:int=0,
):
  """
  按关键词搜索本地资料，可按来源过滤并限制返回数量。
  """
  # 工具包装负责接收参数，Service仍然负责真正的检索业务。
  documents = service.retrieve(query=query,top_k=top_k,source=source,min_content_length=min_content_length)
  return {"documents":documents,"count":len(documents)}

#封装
@tool("search_documents",args_schema = RetrievalRequest)
def mcp_search_documents(
  query: str,
  top_k: int = 3,
  source: str | None = None,
  min_content_length:int=0,
)->dict[str,object]:
  """通过mcp服务检索本地资料。"""
  # 运行协程并取得结果。这里用它连接同步工具函数和异步Client
  return asyncio.run(mcp_search(
    query = query,
    url = "http://127.0.0.1:8051/mcp/",
    top_k = top_k,
    source = source,
    min_content_length = min_content_length,
  ))



def get_retrieval_service():
  return service

@app.post("/retrieve")
async def retrieve(request: RetrievalRequest,retrieval_service:RetrievalService=Depends(get_retrieval_service)):
  try:
    documents = retrieval_service.retrieve(
      query = request.query,
      top_k = request.top_k,
      source=request.source,
      min_content_length = request.min_content_length
    )
    return {"documents":documents,"count":len(documents)}
  except RuntimeError as e:
    raise HTTPException(status_code=503, detail=str(e))

def find_invalid_sources(
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
        source = doc.get("source")
        if not isinstance(source,str):
          raise ValueError("工具文档来源无效")
        source = source.strip()
        if not source:
          raise ValueError("工具文档来源无效")
        allowed_sources.add(source)
  for source in claimed_sources:
    if source not in allowed_sources:
      invalid_sources.append(source)
  # 把检查结果返回给调用者；本函数只使用传进来的两个参数。
  return invalid_sources

         
@lru_cache(maxsize=1)
def get_agent():
  api_key = os.getenv("new_apikey")
  if not api_key:
    raise HTTPException(
      status_code=503,
      detail="服务未配置环境变量 new_apikey",
    )
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
    tools=[mcp_search_documents],
    system_prompt=(
     "你是一个技术资料助手。"
    "涉及本地资料的问题，先使用检索工具。"
    "普通问候或简单计算可以直接回答。"
    "依据本地资料回答时，只使用本次检索正文明确支持的信息。"
    "不要用模型已有知识补充资料中没有的细节。"
    "资料不足以回答的部分，明确说明资料未提供相关信息。"
    "sources只填写本次检索文档的source，不得自行构造来源。"
    "如果检索结果为空，明确说明没有找到本地资料。"
    "不要重复执行相同参数的检索。"
    ),
      # 按AnswerResult组织答案，并由框架解析、校验。
    response_format=ToolStrategy(AnswerResult),
    checkpointer= InMemorySaver(),
  )
  return agnet


def answer_question(question:str,agent,thread_id:str) ->AnswerResult:
#  问答函数
  #question 来自调用者
  result = agent.invoke(
    {"messages":[HumanMessage(content = question)]},
    config={"recursion_limit":10,"configurable":{"thread_id":thread_id}},
  )
 # ToolStrategy 已将最终答案解析成 AnswerResult 对象。
  answer_result = result["structured_response"]
   # 从消息末尾向前找，只收集最新一条用户消息之后的工具结果。
  current_tool_messages=[]
  for message in reversed(result["messages"]):
    if message.type == "human":
      break
    if message.type == "tool":
      current_tool_messages.append(message)
  # 仅用本轮工具结果核对来源。
  invalid_sources = find_invalid_sources(
    current_tool_messages,
    answer_result.sources,
  )
  if invalid_sources: 
    raise ValueError("回答包含把本次检索之外的来源")

  return answer_result
 

  
@app.post("/ask",response_model=AnswerResult)
def ask(
  request: AskRequest,
  agent=Depends(get_agent),
):
  question = request.question.strip()
  if not question: 
    raise HTTPException(status_code=422, detail="请输入问题",)
  thread_id = request.thread_id.strip()
  if not thread_id: 
    raise HTTPException(status_code=422, detail="请输入会话ID",)
  
  try: 
    return answer_question(
      question=question,
      agent=agent,
      thread_id=thread_id,

    )

  except ValueError as e: 
    raise HTTPException(
      status_code=502,
      detail="Agent 返回的结果没有通过校验",
    )from e

  except (APIError, GraphRecursionError, RuntimeError) as e:
    raise HTTPException(
      status_code=503,
      detail="问答服务暂时不可用，请稍后重试",
    ) from e


  


      
if __name__ == "__main__":
    agnet = get_agent()
    question =[
         "什么是agent", 


        "请检索FastAPI，来源限定为langgraph-docs，"
        "最多返回两条，并依据本地资料解释它与LangGraph的关系。",


        "请使用Docker作为关键词检索本地资料，"
        "如果没有匹配资料，请明确说明。",
    ]
    for index, q in enumerate(question, start=1):
     print("\n问题：",q)
  
     # 三个独立演示题分别使用自己的会话，避免历史结果互相影响。
     result = agnet.invoke(
         {"messages": [HumanMessage(content=q)]},
         config={
             "recursion_limit": 10,
             "configurable": {"thread_id": f"cli-demo-{index}"},
         },
     )

     roles = [message.type for message in result["messages"]]
     print("信息角色顺序",roles)

     for message in result["messages"]:
       if(
         message.type == "tool" and
         message.name == "search_documents"
       ):
         print("检索结果",message.content)

     strucured = result["structured_response"]  

     # 函数名后加括号才是调用；返回值invalid_sources是一个列表。
     invalid_sources = find_invalid_sources(
       result["messages"],
       strucured.sources,
     )
     print("不合法来源：", invalid_sources)
     print(
       "伪造来源测试：",
       find_invalid_sources(result["messages"], ["fake-docs"]),
     )

     print("回答：", strucured.answer)
     print("来源：", strucured.sources)

     # model_dump是Pydantic方法，将模型对象转换为字典。
     print("完整结果：", strucured.model_dump())


      
