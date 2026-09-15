from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
def call_chat_completions_api():
    client = OpenAI(
     base_url=os.getenv("OPENAI_BASE_URL"),  # 平台提供的 URL
     api_key=os.getenv("OPENAI_API_KEY"),  # 平台提供的 API-Key
    )

    completion = client.chat.completions.create(
     model="deepseek-v4-flash",  # 模型名称
     messages=[
        {"role": "user", "content": "你好"}
        ],  # 用户输入
        
     )

def call_responses_api():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),base_url=os.getenv("OPENAI_BASE_USER"))
    response = client.responses.create(
        model="deepseek-v4-flash",
        input="明天是什么节日"
    )
    print(response.output_text)

    
call_responses_api()