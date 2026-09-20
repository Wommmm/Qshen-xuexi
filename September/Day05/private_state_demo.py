from typing import TypedDict
from pydantic import BaseModel
from langgraph.constants import START, END
from langgraph.graph import StateGraph
class MyState(TypedDict):
    query:str
    final_answer:str
#定义私有状态，仅在搜索节点和llm节点之间传递数据
class SearchState(TypedDict):
    rag_result:str
    web_search_result:str




def rag_search_node(state:MyState):
    print(state)
    query = state["query"]
    rag_result = f"关于{query}的rag_result"
    return {"rag_result":rag_result,"a_new_key":"a_new_key_value"}

def web_search_node(state:MyState):
    query = state["query"]
    web_search_result = f"关于{query}的web_search_result"
    return {"web_search_result":web_search_result}

def final_answer_node(state:SearchState):
    print('在final_answer_node当中的state',state)
    rag_result = state["rag_result"]
    web_search_result = state["web_search_result"]
    final_answer = f"LLM基于{rag_result}，和{web_search_result}的最终回复"
    return {"final_answer":final_answer}

builder = StateGraph(state_schema=MyState)
builder.add_node(rag_search_node)
builder.add_node(web_search_node)
builder.add_node(final_answer_node)
builder.add_edge(START, "rag_search_node")
builder.add_edge(START,"web_search_node")
builder.add_edge("rag_search_node", "final_answer_node")
builder.add_edge("web_search_node","final_answer_node")
builder.add_edge("final_answer_node", END)
compiled_builder = builder.compile()
res = compiled_builder.invoke({"query":"如何使用LangGraph?"})
print('最终结果为',res)
