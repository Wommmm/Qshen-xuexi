from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import os
import dotenv
dotenv.load_dotenv()
llm = ChatOpenAI(model="deepseek-chat",)

agent = create_agent(
    model=llm,
)
def no_memory_agent():
#第一次调用
    res = agent.invoke({"messages":[{"role":"user","content":"什么是langchain"}]})
    print("第一次调用",res["messages"])

    #第二次调用
    res2 = agent.invoke({"messages":[{"role":"user","content":"我问了你什么"}]})
    print("第二次调用",res2["messages"])


def memory_agent():
    from langgraph.checkpoint.memory import InMemorySaver#引入内存保存器
    from langgraph.checkpoint.sqlite import SqliteSaver
    import sqlite3
    #1
    checkpoint = InMemorySaver()#是进程，存在内存中
    #2
    sqlite_saver = SqliteSaver(conn=sqlite3.connect("./agent_memory.bd",check_same_thread=False))#存在sqlite数据库中
    agent = create_agent(
        model=llm,
       checkpointer = sqlite_saver
    )
    # res = agent.invoke({"messages":[{"role":"user","content":"什么是langchain"}]},config={"configurable":{"thread_id":1}})
    # print("第一次调用",res["messages"])
    
    # 第二次调用传入与第一次调用相同的thread_id,代表使用上一次使用的 消息列表/上下文
    res2 = agent.invoke({"messages":[{"role":"user","content":"我问了你什么"}]},config={"configurable":{"thread_id":1}})
    print("第二次调用",res2["messages"])

if  __name__ == "__main__":
    memory_agent()
    