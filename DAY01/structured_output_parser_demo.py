def use_prompt_demo():
    #0、导包
    #1、定义json结构，使用pydantic定义数据结构
    from pydantic import BaseModel,Field
    #{"prime":[1,2,3],"count":[0,1,2]}，这是所希望的json结构
    class Prime(BaseModel):
        prime: list[int] = Field(description="素数")
        count: list[int] = Field(description="小于该素数的素数个数")
    #2、引用langchain的JsonOutputParser
    from langchain_core.output_parsers import JsonOutputParser

    #3.创建JsonOutputParser实例
    parser = JsonOutputParser(pydantic_object=Prime)
    #4调用大模型，在sytem message当中添加格式化指令
    import os
    from langchain_openai import ChatOpenAI
    from DAY02.config import OPENAI_API_KEY, OPENAI_BASE_URL
    llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL,
        )
    res = llm.invoke([("system",parser.get_format_instructions()),
                      ("user","任意生成5个1000-100000之间素数，并标出小于该素数的素数个数")
                     ])
    #得到json字符串
    print(res.content)

    res = parser.invoke(res.content)
    print(type(res))
    

    from openai import OpenAI
    from langchain_openai import ChatOpenAI
    from pydantic import BaseModel
    #1.定义一个json Schema-结构
    class calendarEvent(BaseModel):
        name: str
        date: str
        participants: list[str]
    import os
    from langchain_openai import ChatOpenAI
    from DAY02.config import OPENAI_API_KEY, OPENAI_BASE_URL
    from openai import OpenAI
    # llm = ChatOpenAI(
    #             model="deepseek-chat",
    #             openai_api_key=OPENAI_API_KEY,
    #             openai_api_base=OPENAI_BASE_URL,
    #         )    
    # res = llm.chat.completions.parse(
    #     messages=[{"role":"user","content":"每天是教师节"}],
    #     response_format=calendarEvent
    # )
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

    res = client.chat.completions.parse(
       messages=[{"role":"user","content":"今天是教师节"}],
       response_format=calendarEvent
       )
    print(res.choices[0].message.parsed)
    print(type(res.choices[0].message.parsed))    

import json
from openai import OpenAI
from pydantic import BaseModel

def use_model_structured_output_demo():
    """
    使用DeepSeek大模型实现结构化输出示例
    注意：DeepSeek不支持openai原生的parse()方法(json_schema模式)
    采用create + response_format=json_object 实现，提示词约束输出字段，再用Pydantic做本地校验解析
    输出目标结构：日历事件CalendarEvent，包含name事件名称、date日期、participants参与者数组
    缺陷：json_object仅保证返回合法json，服务端不会校验schema，字段正确性依赖prompt约束
    """
    from openai import OpenAI
    from pydantic import BaseModel

    #1.定义一个json Schema-结构
    class calendarEvent(BaseModel):
        name: str
        date: str
        participants: list[str]

    from DAY02.config import OPENAI_API_KEY, OPENAI_BASE_URL
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    res = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"user","content":"生成教师节日历事件，输出json。必须包含三个字段：name(事件名称), date(日期), participants(参与者数组)，不要其他字段。"}],
        response_format={"type":"json_object"}
    )
    parsed = calendarEvent(**json.loads(res.choices[0].message.content))

    print(parsed)
    print(type(parsed))


def use_model_output_use_langchain():
    """
    LangChain with_structured_output 结构化输出演示，适配DeepSeek大模型
    关键点：
    1. DeepSeek不支持json_schema模式，必须设置method="json_mode"，底层使用response_format=json_object
    2. json_object接口强制要求提示词文本中必须包含json关键字，否则直接返回400错误
    3. json_object仅保证返回合法JSON字符串，服务端不会校验字段，字段校验由本地Pydantic完成
    4. 警告提示Core Pydantic V1 functionality...为langchain库版本兼容警告，不是错误，不影响程序运行
    输出对象为pydantic模型实例，可以直接通过 res.name res.date res.participants 访问属性
    注意：如果未给模型说明数组内容，数组可能返回空列表，需要在prompt补充生成示例数据的要求
    """
    import os
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
    from langchain_core.output_parsers import JsonOutputParser
    from pydantic import BaseModel, Field
    import os
    from langchain_openai import ChatOpenAI
    from DAY02.config import OPENAI_API_KEY, OPENAI_BASE_URL
    #1构建llm对象
    llm = ChatOpenAI(
                model="deepseek-chat",
                openai_api_key=OPENAI_API_KEY,
                openai_api_base=OPENAI_BASE_URL,
            )
    #2构建schema结构
    class calendarEvent(BaseModel):
            name: str
            date: str
            participants: list[str]

    #3调用llm.with_structur_output()方法
    new_llm = llm.with_structured_output(schema=calendarEvent,method="json_mode")

    #4用new_llm调用invoke
    res = new_llm.invoke([{"role":"user","content":"2026年9.10号请生成日历事件，输出json，必须包含name、date、participants三个字段"}])

    print(type(res))
    print(res)


     
from langchain_core.output_parsers.xml import XMLOutputParser      


    
    