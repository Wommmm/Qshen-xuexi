#图内外数据传递
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from typing import TypedDict

from yarl import Query
load_dotenv()
def stream_moed_messages_demo ():
    llm = ChatOpenAI(model="deepseek-chat")
    #单独的chatmodel的实例要流式输出，需要调用llm.stream

    class State(TypedDict):
        llm_message: list
        query: str

    def llm_node(state:State): 
        """
       模拟一个LLM节点
       """
        qery = state["query"]  
        #只要通过graph.stream()的时候，并且stream_moe为messages，llm_message就会变成一个流式输出
        res = llm.invoke(qery)
        return {"llm_message": res.content}

    builder = StateGraph(state_schema=State)   

    builder.add_node(llm_node)
    builder.add_edge("__start__", "llm_node")
    graph = builder.compile()

    for ai_message_chunk,metadata in graph.stream({"query":"什么是langgraph"},stream_mode ="messages"):
        print(ai_message_chunk.content,end="")
        # print(metadata)


class State(TypedDict):
    llm_message: list
    query: str
    rag_search: str

def llm_node(state:State): 
     """
     模拟一个LLM节点
     """       
     query = State["query"]  
        #只要通过graph.stream()的时候，并且stream_moe为messages，llm_message就会变成一个流式输出
     res = "调用结果"

     return {"llm_message": res}

def rag__node(state:State):
    query = state["query"]
    rag_search = f"根据用户问题{query},从知识库中检索相关内容"
    return {"rag_search": rag_search}

builder = StateGraph(state_schema=State)   
builder.add_node(llm_node)
builder.add_node(rag__node)
builder.add_edge("__start__", "llm_node")
builder.add_edge("llm_node", "rag__node")
graph = builder.compile()
for state in graph.stream({"query":"什么是langgraph"},stream_mode ="values"):
    print(state)

