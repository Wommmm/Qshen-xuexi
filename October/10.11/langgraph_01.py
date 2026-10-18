from typing import TypedDict,Annotated
from langgraph.graph import StateGraph,START,END
from langchain.messages import HumanMessage,AIMessage,AnyMessage,ToolMessage
from langgraph.graph.message import add_messages
from langchain.tools import tool
import os
from langchain_openai import ChatOpenAI
from fastapi_retrieval_demo import search_documents
from langgraph.prebuilt import ToolNode


# 检索来源
DOCUMENTS = [
    {
        "id": "doc-1",
        "content": "FastAPI 用于构建 HTTP API",
        "source": "fastapi-docs",
    },
    {
        "id": "doc-2",
        "content": "LangChain 可以将 Python 函数包装成工具",
        "source": "langchain-docs",
    },
]


# TypedDict 声明字典有哪些字段、各字段是什么类型。
class RetrievalState(TypedDict):
    tool_rounds: int
    query: str             # 当前检索关键词
    documents: list[dict]  # 检索得到的文档
    answer: str            # 资料展示或无结果说明；当前不调用模型
    # 消息列表收到更新时，由 LangGraph 使用 add_messages 合并。
    messages: Annotated[list[AnyMessage],add_messages]




def normalize_query(state: RetrievalState) ->dict:
#读取关键字
    keyword = state["query"].strip().lower()
    return {"query":keyword}


def retrieve_documents(state: RetrievalState) ->dict:
    keyword = state["query"]
    if not keyword:
        return {"documents":[]}
    results =[]
    for doc in DOCUMENTS:
        if keyword in doc["content"].lower():
            results.append(doc)
    return {"documents":results}        



def format_answer(state: RetrievalState) -> dict:
    # 先逐条取正文，再使用换行符连接，便于观察每一步。
    contents = []
    for doc in state["documents"]:
        contents.append(doc["content"])
    answer = "\n".join(contents)
    return {
        "answer": answer,
        "messages":[AIMessage(content=answer)],
    }

def no_documents(state: RetrievalState)->dict:
    answer = "没有找到相关资料。"  
    return {
        "answer": answer,
        "messages":[AIMessage(content=answer)],
    }  


def route_after_retrieval(state: RetrievalState) -> str:
    # 路由返回分支标识；下方映射将它对应到实际节点。
    MAX_TOOL_ROUNDS = 2
    return "found" if state["documents"] else "empty"

model = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("new_apikey"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    timeout=60,
    max_retries=0,
)

model_with_tools = model.bind_tools([search_documents])

MAX_TOOL_ROUNDS = 2
def route_after_model(state: RetrievalState) -> str:
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "done"
    rounds = state["tool_rounds"]
    if rounds >= MAX_TOOL_ROUNDS:
        return "limit"
    return "tools"
   

def call_model(state: RetrievalState)->dict:
    messages = state["messages"]
    reply = model_with_tools.invoke(messages)
    return {"messages": [reply]}

def count_tool_round(state:RetrievalState)->dict:
    rounds = state["tool_rounds"]
    return {"tool_rounds":rounds+1}


def limit_reached(state:RetrievalState) ->dict:
    messages = []
    for call in state["messages"][-1].tool_calls:
        messages.append(ToolMessage(
            content="已经达到轮数上限",
            tool_call_id=call["id"],status="error"
        ))
    messages.append(AIMessage(
        content="已经达到轮数上限"
    ))
    return {"messages":messages}  

tool_node = ToolNode([search_documents],handle_tool_errors= True,)

builder = StateGraph(state_schema=RetrievalState)

builder.add_node("model", call_model)
builder.add_node("tools", tool_node)
builder.add_node("count_tool_round",count_tool_round)
builder.add_node("limit_reached",limit_reached)

builder.add_edge(START, "model")
builder.add_conditional_edges("model", route_after_model,{"tools": "tools", "done": END,"limit": "limit_reached"})
builder.add_edge("tools", "count_tool_round")
builder.add_edge("count_tool_round", "model")
builder.add_edge("limit_reached", END)
graph = builder.compile()

if __name__ == "__main__":
    initial_state: RetrievalState = {
        "query": " FastAPI ",
        "documents": [],
        "answer": "",
        "tool_rounds":0,
        "messages":[HumanMessage(content="请检索FastAPI")]
    }
    
    result = graph.invoke(initial_state)

    print("图执行后的状态：", result)

    tool_call_count = 0
    for message in result["messages"]:
        if isinstance(message,AIMessage):
            for call in message.tool_calls:
                print("调用了的工具",call["name"],"参数",call["args"])
                tool_call_count += 1
    print("调用了工具次数：",tool_call_count)            


    old_reply = result["messages"][-1]   
    new_reply = AIMessage(
        content = "修订后的回答,Fastapi可以用于构建http api",
        id = old_reply.id,
    )
    updated_messages = add_messages(
        result["messages"],
        [new_reply],
    )

    print("更新前消息数：", len(result["messages"]))
    print("更新后消息数：", len(updated_messages))

    for message in updated_messages:
        print(message.type, message.content)

    
