from typing import TypedDict,Annotated
from langgraph.graph import StateGraph,START,END
from langchain.messages import HumanMessage,AIMessage,AnyMessage
from langgraph.graph.message import add_messages,StateGraph,START,END


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
    return "found" if state["documents"] else "empty"


builder = StateGraph(state_schema =RetrievalState)
builder.add_node("normalize",normalize_query)   
builder.add_node("retrieve",retrieve_documents)
builder.add_node("answer", format_answer)
builder.add_node("no_documents", no_documents)

builder.add_edge(START, "normalize")
builder.add_edge("normalize", "retrieve")
builder.add_conditional_edges(
    "retrieve",
    route_after_retrieval,
    {"found": "answer", "empty": "no_documents"},
)
builder.add_edge("answer", END)
builder.add_edge("no_documents", END)
        
graph = builder.compile()   

if __name__ == "__main__":
    initial_state: RetrievalState = {
        "query": " FastAPI ",
        "documents": [],
        "answer": "",
        "messages":[HumanMessage(content="请检索FastAPI")]
    }
    result = graph.invoke(initial_state)

    print("图执行后的状态：", result)

    for message in result["messages"]:
        print(message.type,message.content)

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

    
