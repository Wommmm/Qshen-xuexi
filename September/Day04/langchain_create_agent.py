from langchain.tools import tool
from langchain.agents import create_agent 
from langchain_openai import ChatOpenAI   
from dotenv import load_dotenv
import os
from langchain.messages import AIMessage
load_dotenv(r"D:\LANGCHANINDEMO\september\.env")
#1.构建一个agent实例

#1.1定义一个模型
llm = ChatOpenAI(model="deepseek-chat")
#1.2定义模型能使用的工具
@tool(description="获取城市在特定日期的天气")
def get_weather(city: str, date: str):
    return f"城市{city}在{date}的天气下雨"

agent = create_agent(model=llm,
                     tools=[get_weather]
                     )

# 2.调用agent，获取结果
res = agent.invoke({"messages":[{"role": "user", "content": "在广西来宾的2026-09-01的天气"}]})
res = agent.invoke({"messages":[{"role": "user", "content": "你还记得我问你的问题吗？"}]})
print(res["messages"][-1].content)

#3.通过流式调用agent
for chunk in  agent.stream({"messages":[{"role": "user", "content": "在广西来宾的2026-09-01的天气"}]},stream_mode="messages",):
       print(chunk[0].content,end="",flush=True) 

    