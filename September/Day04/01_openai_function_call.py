from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv(r"D:\LANGCHANINDEMO\september\.env")

# 1、工具函数
def get_weather(city,date):
    return f"{city} on {date} is cloudy with a chance of rain."

messages = [
    {"role": "user", "content": " 北京 在 2024-12-25?的天气怎么样"}
]



# 2、工具的 JSON Schema（注意是列表） 
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取城市在特定日期的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称, e.g. 北京"},
                    "date": {"type": "string", "description": "查询日期, e.g. 2023-12-25"},
                },
                "required": ["city", "date"],
            },
        },
    }
]
#3.调用
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
)

print(resp.choices[0].message.tool_calls)

messages.append(resp.choices[0].message)
#4.解析OpenAI返回的tool_call，具体调用get_weather函数
too_call_arguments = resp.choices[0].message.tool_calls[0].function.arguments#解析
to_call_id = resp.choices[0].message.tool_calls[0].id
#构建一个tool message
import json
parameter_dict = json.loads(too_call_arguments)
city = parameter_dict["city"]
date = parameter_dict["date"]
weather = get_weather(city, date)
messages.append(
    {
        "role": "tool",       
        "tool_call_id":to_call_id,
        "name": "get_weather",
        "content": weather,
    }
)

#将JSON字符串解析成dict，获取到每个参数


#5.将结果返回给OpenAI
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
)
print(response.choices[0].message.content)   # 改成 response


