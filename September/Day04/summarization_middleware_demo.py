from langchain_openai import ChatOpenAI
import os
import dotenv
dotenv.load_dotenv()
#1.从langchain引入自带的消息摘要中间件
from langchain.agents.middleware import SummarizationMiddleware
summarization_llm =ChatOpenAI(model="deepseek-chat",)

#2.构造一个summarizationMiddleware实例
summarization_middleware = SummarizationMiddleware (
    model=summarization_llm,
    #有三种不同的触发条件
    #1.tonken到达多少后做摘要（"tonkens"，200）
    #2.消息长度到达多少后做摘要（"message"，100）
    #3.当前token总数达到了模型最大能支持的上下文长度的比例的多少后做摘要（"fraction"，0.5）
    trigger = ("tokens", 200),
    keep = ("messages",3)
)

#3.构造一个agent
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
cki = InMemorySaver()
llm = ChatOpenAI(model="deepseek-chat")
agent = create_agent(
    model = llm, #推理使用更大模型
    middleware = [summarization_middleware],
    checkpointer = cki
)
res = agent.invoke({"messages":[{"role":"user","content":"what is langchain?"}]},config={"configurable":{"thread_id":1}})
print("第一次",res["messages"])
res = agent.invoke({"messages":[{"role":"user","content":"请用中文回答我"}]},config={"configurable":{"thread_id":1}})
print("第二次",res["messages"])
res = agent.invoke({"messages":[{"role":"user","content":"什么是协程"}]},config={"configurable":{"thread_id":1}})
print("第三次",res["messages"])