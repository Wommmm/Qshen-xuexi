# 必须放在最顶部！先设置镜像，再导入包
import os
# 国内镜像，写在 import huggingface_hub 前面
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from huggingface_hub import snapshot_download

repo_id = "BAAI/bge-base-zh-v1.5"
local_dir = r".\assets\models\bge-base-zh-v1.5"

snapshot_download(
    repo_id=repo_id,
    local_dir=local_dir,
    local_dir_use_symlinks=False
)
