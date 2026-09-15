import os
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from DAY02.config import OPENAI_API_KEY, OPENAI_BASE_URL


# Pydantic数据模型：定义期望提取的会议结构化数据格式
class calendarEvent(BaseModel):
    name: str               # 会议名称
    date: str               # 会议时间日期
    participants: list[str] # 参会人员列表


def extract_calendar_event(question: str) -> calendarEvent:
    """
    从用户文本中提取会议事件信息，返回Pydantic结构化对象
    :param question: 用户输入的自然语言文本，描述会议信息
    :return: calendarEvent 会议结构化对象
    """
    # 构建聊天提示模板，system定义解析规则
    # {format_instructions} 占位符，JsonOutputParser会自动填充模型字段说明
    template = ChatPromptTemplate.from_messages(
        messages=[
            ("system", "提取会议信息，输出json，不要多余文字。{format_instructions}"),
            ("user", "{input_question}")
        ]
    )

    # 实例化大模型对象，对接deepseek‑chat接口
    llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_BASE_URL,
    )

    # JSON输出解析器，替代with_structured_output，规避接口兼容问题
    parser = JsonOutputParser(pydantic_object=calendarEvent)

    # LCEL流水线：提示模板 → 大模型调用 → json解析
    chain = template | llm | parser

    # 执行调用，传入用户问题，得到字典结果
    res_dict = chain.invoke({"input_question": question})

    # 字典解包转换为Pydantic模型实例返回
    event = calendarEvent(**res_dict)
    return event


def runnable_parallel_demo():

    import os
    from langchain_core.prompts import PromptTemplate
    from langchain_core.runnables import RunnableParallel
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatOpenAI(
           model="deepseek-chat",
           openai_api_key=OPENAI_API_KEY,
           openai_api_base=OPENAI_BASE_URL,
       )
    #SrtOutputParser:把llm.invoke得到的AIMessage对象，提取出content内容
    english_chain = (
        PromptTemplate.from_template("把这个句子{topic}翻译成英文") | llm | english_chain.invoke.content({"topic":"你好"})
    )
    korean_chain = (
        PromptTemplate.from_template("把这个句子{topic}翻译成韩文") | llm | StrOutputParser()
    )

    map_chain = RunnableParallel(english=english_chain, korean=korean_chain)




# 测试调用

    