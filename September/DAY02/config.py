import os
from dotenv import load_dotenv, find_dotenv

# 加载 .env 文件（只执行一次）
load_dotenv(find_dotenv())

# 将常用变量直接导出，方便直接使用
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

