import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from huggingface_hub import snapshot_download
#下载模型

snapshot_download(
    repo_id="BAAI/bge-m3",
    local_dir=r"assets\models\bge-m3",
    ignore_patterns=["imgs/*", "*.DS_Store"], # 跳过图片文件夹和mac残留文件，解决403
    max_workers=4 # 减少并发线程，降低报错概率
)
