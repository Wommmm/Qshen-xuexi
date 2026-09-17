from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage,ToolMessage,HumanMessage
from pydantic import BaseModel,Field
import os
from dotenv import load_dotenv
load_dotenv()


class calendarEvent(BaseModel):
    """
 BaseModel 是 Pydantic 提供的基类，CalendarEvent 继承该类；
 为 city、date 添加类型约束，并通过 Field 函数配置字段说明、别名、校验规则等。
 """
    city: str = Field(description="城市名称")
    date: str = Field(description="日期，格式为YYYY-MM-DD")

@tool(description="获取指定城市的天气信息", args_schema=calendarEvent)
def get_weather(city: str, date: str):
    """获取城市在特定日期的天气"""
    return f"城市{city}在{date}的天气是晴朗的"

llm = ChatOpenAI(model="deepseek-chat")
#在模型上绑定工具，得到新llm实例,后续调用新ai接口时，自动传递tools参数
llm_with_tools = llm.bind_tools([get_weather])
human_message =HumanMessage(content="在广西的2026-09-01的天气")
res = llm_with_tools.invoke([human_message])
ai_message = res
too_id = res.tool_calls[0]["id"]
print(res)

#2.解析AIMessage,具体调用get_weather工具
too_call = res.tool_calls[0]["args"]
tool_res = get_weather.invoke(too_call)

#封装 Tool Message
tool_message = ToolMessage(tool_call_id=too_id,content=tool_res)
llm_second_res = llm_with_tools.invoke([human_message,ai_message,tool_message])
print(llm_second_res)
