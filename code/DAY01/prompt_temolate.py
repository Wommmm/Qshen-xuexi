from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages(
    messages=[
        ("system","你是一个专业的翻译"),
        ("user",'请把这句话翻译{sentence}成英文')
    ]
)

from langchain_openai import ChatOpenAI
import os
from DAY02.config import OPENAI_API_KEY, OPENAI_BASE_URL
llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL,
        )

res = llm.invoke(template.invoke({"sentence":"跟我解释一下什么是RAG"}))
print(res.content)
