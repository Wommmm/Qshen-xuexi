from openai import OpenAI
from dotenv import load_dotenv
import os

# 读取 .env 里的配置（API key 和接口地址），不写这行 os.getenv 就读不到
load_dotenv(r"D:\LANGCHANINDEMO\september\.env")

# 1、工具函数
# 这是模型可以调用的"能力"。注意：模型不会执行它，只负责点名要调它，
# 真正的执行在第 58 行（你的代码调用它）
def get_weather(city,date):
    return f"{city} on {date} is cloudy with a chance of rain."

# 对话历史。每条消息是一个字典：
#   role    = 谁说的（user 用户 / assistant 模型 / tool 工具结果）
#   content = 说了什么
messages = [
    {"role": "user", "content": " 北京 在 2024-12-25?的天气怎么样"}
]



# 2、工具的 JSON Schema（注意是列表）
# 这段是 Function Calling 的核心：告诉模型"你有哪些工具、每个工具要什么参数"
# 模型完全靠 description 来决定要不要用这个工具，所以描述要写清楚
tools = [
    {
        "type": "function",          # 固定值，表示这是个函数工具
        "function": {
            "name": "get_weather",   # 工具名，模型返回时会带回来
            "description": "获取城市在特定日期的天气",   # 功能描述，很重要
            "parameters": {          # 参数的 JSON Schema
                "type": "object",
                "properties": {      # 逐个声明参数及类型
                    "city": {"type": "string", "description": "城市名称, e.g. 北京"},
                    "date": {"type": "string", "description": "查询日期, e.g. 2023-12-25"},
                },
                "required": ["city", "date"],   # 必填参数
            },
        },
    }
]  # tools 是列表，因为可以声明多个工具
#3.调用
# client 是"连接器"，负责把请求发到服务器、把结果拿回来
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),   # 密钥，从 .env 读（身份认证用）
    base_url=os.getenv("OPENAI_BASE_URL"), # 接口地址，这里是 DeepSeek
)

# 第一次请求：把问题和工具清单一起发给模型，让它决定要不要用工具
resp = client.chat.completions.create(
    model="deepseek-chat",   # 用哪个模型
    messages=messages,       # 对话历史
    tools=tools,             # 可用工具清单
)

# 打印模型想干什么。链式访问拆解：
#   resp            整个响应
#     .choices      候选回复列表（可以同时要多个答案，所以是列表）
#       [0]         取第一个（默认只要一个，所以固定 [0]）
#         .message  模型说的这条消息
#           .tool_calls   消息里要求调用的工具（也是列表，可能一次调多个）
# 若模型觉得不用工具，这里就是 None
print(resp.choices[0].message.tool_calls)

# 把模型的回复加入对话历史（不能漏！否则下一轮它不知道自己说过要调工具）
messages.append(resp.choices[0].message)
#4.解析OpenAI返回的tool_call，具体调用get_weather函数
# 取出"参数"：注意这是 JSON 字符串，不是字典
# 例如：'{"city": "北京", "date": "2024-12-25"}'
# 网络传输只能用文本，所以第 55 行要转换
too_call_arguments = resp.choices[0].message.tool_calls[0].function.arguments
# 取出这次调用的编号（类似快递单号），第 62 行返回结果时要带上它，
# 模型才知道"这个结果对应哪一次调用"
to_call_id = resp.choices[0].message.tool_calls[0].id
#构建一个tool message
import json
# JSON 字符串 → Python 字典
#   '{"city":"北京","date":"2024-12-25"}'  →  {"city":"北京", "date":"2024-12-25"}
parameter_dict = json.loads(too_call_arguments)
# 从字典里取出具体的值
city = parameter_dict["city"]     # "北京"
date = parameter_dict["date"]     # "2024-12-25"
# 真正执行函数！这一步是你的 Python 在跑，不是模型在跑
weather = get_weather(city, date)
# 把工具结果包装成 tool message 加入历史。
# 字段名是协议规定死的，不能自己起：
#   role         → 固定 "tool"
#   tool_call_id → 对应哪次调用（用第 52 行拿到的编号）
#   name         → 工具名
#   content      → 函数执行的【结果】（不是参数！）
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
# 第二次请求：这次不传 tools 了，工具已经执行完，
# 现在只让模型"看着结果，用人话回答用户"
# 此时 messages 里有三条：用户提问 + 模型要调工具 + 工具结果
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
)
# 打印最终答案。注意用的是 response（第二次请求的结果），
# 不是 resp（第一次的，它只有 tool_calls 没有 content）
print(response.choices[0].message.content)   # 改成 response

# ============================================================
# 整个流程一句话：
#   模型不执行代码，它只"决定"；你负责"执行"，再把结果喂回去让它组织成人话。
#
# 口诀：
#   ① 带着 tools 问一次     → 模型说"我要调 X，参数是 Y"
#   ② 你真的执行 X(Y)       → 拿到结果
#   ③ 结果塞回 messages     → 带上 tool_call_id
#   ④ 再问一次（不带 tools）→ 模型给出最终回答
# ============================================================
