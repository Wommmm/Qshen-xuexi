# 计算请求摘要
import hashlib
import json

def hash_payload(payload:dict) -> str:
    text = json.dumps(
        payload,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
    )
    return hashlib.sha256(text.encode('utf-8')).hexdigest()