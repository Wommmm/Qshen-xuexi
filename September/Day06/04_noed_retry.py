#节点重试
from typing import TypedDict,Annotated
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy
attempt = 0
class MyState(TypedDict):

    llm_message:str


def llm_node(state:MyState)->dict:   
     """
     模拟一个不稳定的LLM节点
     """
     global attempt
     print(f"LLM节点第{attempt}次尝试")
     if attempt < 3:
          attempt += 1
          raise ConnectionError("LLM节点异常")
     print("LLM节点第三次调用") 
     return {"llm_message": "LLM节点正常"} 

builder = StateGraph(state_schema=MyState)     
#RetryPolicy:
 #针对什么类型异常进行重试
 #重试的次数
 #重试到底间隔：指数退避策略:1s,2s,4s,8s,16s....
builder.add_node(llm_node,retry_policy=RetryPolicy())

builder.add_edge("__start__","llm_node")

graph = builder.compile()

graph.invoke({})
