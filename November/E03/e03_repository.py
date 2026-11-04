# 在同一事务中保存批次与明细
from sqlalchemy.orm import Session

from e03_models import RunItem, RunRecord
from e03_db import engine

def save_run(result:dict, payload_hash:str):
    with Session(engine) as session:
        with session.begin():
            # 属于同一个事务的数据库操作
            record = RunRecord( 
                request_id = result["request_id"],
                payload_hash = payload_hash,
                status = result["status"],
                result = result
            )
            session.add(record)
            #先将主记录写入当前事物，让后续的明细能引用
            session.flush()
            for position,item in enumerate(result["items"]):
                detail = RunItem(
                    request_id = result["request_id"],
                    item_id = item["id"],
                    status = item["status"],
                    position = position,
                    error_code = item["error_code"]
                )
                session.add(detail)