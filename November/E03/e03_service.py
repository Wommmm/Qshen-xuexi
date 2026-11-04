from November.E01.e01_models import RunRequest
from November.E02.e02_worker import execute_batch

from e03_payload import hash_payload
from e03_repository import get_run, save_run

# 自定义异常，专门表示同 ID 不同内容
class RequestConflictError(Exception):
    pass


async def submit_run(raw_payload:dict):
    payload = RunRequest.model_validate(raw_payload).model_dump()

    payload_hash = hash_payload(payload)

    existing = get_run(payload["request_id"])

    if existing is not None:
        if existing["payload_hash"] != payload_hash:
            raise RequestConflictError("相同批次的请求id内容不同")

        return existing["result"]

    result = await execute_batch(**payload)
    save_run(result, payload_hash)
    return result
        
