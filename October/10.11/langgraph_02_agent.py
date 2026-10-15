import os
from langchain_openai import ChatOpenAI
from fastapi_retrieval_demo import answer_question,ask,find_invalid_sources,get_agent,get_retrieval_service,search_documents
from langchain.messages import SystemMessage,HumanMessage
from langgraph.graph import MessagesState,StateGraph,START,END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
api_key = os.getenv("new_apikey")

if not api_key:
    raise RuntimeError("请设置环境变量")

model = ChatOpenAI(
    model="qwen-plus",
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    timeout=60,
    max_retries=0,
)

tools = [search_documents]
model_with_tools = model.bind_tools(tools)

def call_model(state:MessagesState)->dict:
    # 系统消息助手要求
    messages = [
        SystemMessage(
            content=(
                "你是本地资料助手，资料问题先调用检索工具。"
                "得到工具结果后，只依据检索正文回答。"
                "没有匹配资料时如实说明。"
                "不要重复执行相同参数的检索。"
            )
        )
    ]
    for message in state["messages"]:
        messages.append(message)
    model_reply = model_with_tools.invoke(messages)
    return {"messages": [model_reply]}

builder = StateGraph(MessagesState)
builder.add_node("call_model",call_model)
builder.add_node("tools",ToolNode(tools))

builder.add_edge(START,"call_model")
builder.add_conditional_edges("call_model",tools_condition)
builder.add_edge("tools","call_model")
checkpointers= InMemorySaver()
graph = builder.compile(checkpointer=checkpointers)


if __name__ == "__main__":
    session_config ={
        "configurable":{"thread_id":"session-001"},
        "recursion_limit":5,
    }
    questions =[
        "我叫张飞，记住这个名字",
        "我叫什么名？",
    ]
    for q in questions:
        result = graph.invoke(
            input = {"messages":[HumanMessage(content=q)]},
            config=session_config,
        )
    other_config = {
        "configurable":{"thread_id":"session-001"},
        "recursion_limit":5
    }
    other_result = graph.invoke(
        {"messages":[HumanMessage(content= "我是谁？")]},
        config = other_config
    )
    # get_state() 读取指定会话的状态快照。
    snapshot = graph.get_state(other_config)

    # values 是快照中保存的状态字典。
    for message in snapshot.values["messages"]:
        print(message.type, message.content)



    
    
