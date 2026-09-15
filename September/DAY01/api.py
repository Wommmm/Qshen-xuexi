

def apii():
 import os
 from dotenv import load_dotenv, find_dotenv
 from langchain_openai import ChatOpenAI
 import os
 from DAY02.config import OPENAI_API_KEY, OPENAI_BASE_URL
# 加载 .env 文件（只执行一次）
 load_dotenv(find_dotenv())
 llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=OPENAI_API_KEY,
            openai_api_base=OPENAI_BASE_URL,
        )
 return llm