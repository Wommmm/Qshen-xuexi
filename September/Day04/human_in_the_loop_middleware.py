from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool


@tool(description="获取指定城市的天气")
def get_weather(city: str, date: str) -> str:
    return f"城市{city}在{date}的天气是晴朗的"

@tool(description="转账金额到指定人")
def transfer_money(amount:float,to:str) -> str:
    return f"成功向{to}转账{amount}元"

#定义一个HumanInTheLoopMiddleware,中断"transfer_money"
loop_middleware = HumanInTheLoopMiddleware(interrupt_on={"get_weather":False,"transfer_money":True})

#创建一个agent
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import os
import dotenv
from langgraph.checkpoint.memory import InMemorySaver
dotenv.load_dotenv()
agent = create_agent(model="deepseek-chat",
                     tools=[get_weather,transfer_money],
                     middleware=[loop_middleware],
                     checkpointer=InMemorySaver(),
)

#4，调用agent

#4.1
res = agent.invoke({"messages":[{"role":"user","content":"今天北京的天气如何"}]},config={"configurable":{"thread_id":1}})
print(res)
print("="*50)
#4.2让agent调用transfer_money
res = agent.invoke({"messages":[{"role":"user","content":"帮我转账100元到张三"}]},config={"configurable":{"thread_id":1}})
print(res)

#5.解析__interrupt__
interrupt_info = res["__interrupt__"]
interrupt = interrupt_info[0]
#获取到模型调用工具的参数
inteerrupt_tool_args = interrupt.value["action_requests"][0]["args"]
inteerrupt_tool_name = interrupt.value["action_requests"][0]["name"]
print("工具参数为",inteerrupt_tool_args)
print("工具名称为",inteerrupt_tool_name)

#审核完成，让工具调用继续执行下去
from langgraph.types import Command
# "type":"approve"，"reject"，"deit"，可以选三个参数，一个接受一个拒绝一个修改
res = agent.invoke(Command(resume={"decisions":[{"type":"approve",}]}),config={"configurable":{"thread_id":1}})
print(res)

