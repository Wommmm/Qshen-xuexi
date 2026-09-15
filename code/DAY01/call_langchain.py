import os
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage   
from dotenv import load_dotenv
import asyncio

load_dotenv()  # 加载 .env 文件中的环境变量

async def call_llm_async_demo():#异步调用
 
    llm_model = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_BASE_URL"),
    )

    message_list = [
        SystemMessage(content="你是一个翻译"),
        HumanMessage(content="你能为我做什么")
    ]
    response = await llm_model.ainvoke(message_list)
    print(response.content)

    

if __name__ == "__main__":    
     asyncio.run(call_llm_async_demo())  
       
