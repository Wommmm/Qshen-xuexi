from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage,ToolMessage,HumanMessage
from pydantic import BaseModel,Field
import os
from dotenv import load_dotenv
# 读取 .env 里的密钥和接口地址（不写这行，下面 ChatOpenAI 就读不到配置）
load_dotenv()


# 用 Pydantic 定义"工具需要哪些参数"
# BaseModel 是 Pydantic 的基类，继承它就能声明字段和类型
class calendarEvent(BaseModel):
    """
 BaseModel 是 Pydantic 提供的基类，CalendarEvent 继承该类；
 为 city、date 添加类型约束，并通过 Field 函数配置字段说明、别名、校验规则等。
 """
    # description 会传给大模型，告诉它这个字段是什么意思
    city: str = Field(description="城市名称")
    date: str = Field(description="日期，格式为YYYY-MM-DD")

# @tool 装饰器：把普通函数变成"大模型可以调用的工具"
#   description  → 告诉模型这个工具干什么（模型靠它判断要不要用）
#   args_schema   → 参数结构，LangChain 会自动转成 JSON Schema 发给模型
# 加上这个装饰器后，函数既能被模型调用，也能用 .invoke() 手动调用
@tool(description="获取指定城市的天气信息", args_schema=calendarEvent)
def get_weather(city: str, date: str):
    """获取城市在特定日期的天气"""
    return f"城市{city}在{date}的天气是晴朗的"

# 创建大模型（这里没显式传 key 和地址，靠 .env 里的环境变量自动读取）
llm = ChatOpenAI(model="deepseek-chat")
#在模型上绑定工具，得到新llm实例,后续调用新ai接口时，自动传递tools参数
# bind_tools 不会改动原 llm，而是返回一个"带了工具"的新实例
llm_with_tools = llm.bind_tools([get_weather])
# HumanMessage = 用户发的消息
human_message =HumanMessage(content="在广西的2026-09-01的天气")
# 第一次调用：把问题发给模型，让它决定要不要用工具
# 注意：invoke() 只接受 字符串 / 消息列表 / PromptValue，
#       单个 HumanMessage 对象会报错，所以要用 [ ] 包起来
res = llm_with_tools.invoke([human_message])
# res 是 AIMessage（模型的回复），里面可能有 tool_calls
ai_message = res
# 取出本次工具调用的编号，后面返回结果时要靠它对上号
too_id = res.tool_calls[0]["id"]
print(res)

#2.解析AIMessage,具体调用get_weather工具
# 取出模型给的参数，是一个字典，如 {"city": "广西", "date": "2026-09-01"}
too_call = res.tool_calls[0]["args"]
# 真正执行工具函数（这一步是 Python 在跑，不是模型）
# 参数用 ** 展开：get_weather(city="广西", date="2026-09-01")
# 也可以写成 get_weather.invoke(too_call)
tool_res = get_weather.invoke(too_call)

#封装 Tool Message
# ToolMessage = 工具返回的结果
#   tool_call_id → 对应哪一次调用（用上面拿到的 too_id）
#   content      → 函数执行的结果（不是参数）
tool_message = ToolMessage(tool_call_id=too_id,content=tool_res)
# 第二次调用：把"用户提问 + 模型要调工具 + 工具结果"一起发过去
# 模型看着结果，组织成自然语言回答
llm_second_res = llm_with_tools.invoke([human_message,ai_message,tool_message])
print(llm_second_res)

# ============================================================
# 本文件与 01（原生 openai SDK）的区别：
#
#   原生 SDK：自己写 tools 的 JSON Schema、自己 json.loads 解析参数、
#             自己拼 messages 列表  → 步骤多，但每一步都看得见
#
#   LangChain：@tool 装饰器自动生成 Schema，bind_tools 自动带 tools，
#              invoke 直接传消息对象，工具用 .invoke() 执行
#              → 代码少，但底层还是同一套 Function Calling 流程
#
# LangChain 的 invoke() 输入规则（踩过坑）：
#   ✅ "字符串"
#   ✅ [HumanMessage, AIMessage, ToolMessage]   ← 列表
#   ❌ 单个 HumanMessage（必须包成列表）
# ============================================================
