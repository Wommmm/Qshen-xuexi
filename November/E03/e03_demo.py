# 完整保存实验：复用 E01 校验、E02 执行，调用 E03 保存并读回核对。
import asyncio
import json
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch
import e03_service
from copy import deepcopy
from sqlalchemy.exc import IntegrityError

from sqlalchemy import select
from sqlalchemy.orm import Session

from November.E01.e01_models import RunRequest
from November.E02.e02_worker import execute_batch

from e03_db import engine, init_db
from e03_models import RunRecord, RunItem
from e03_payload import hash_payload
from e03_repository import save_run


async def main():
    scenario_path = (
        Path(__file__).resolve().parents[2]
        / "学习计划"
        / "练习数据"
        / "工程场景.json"
    )

    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))

    # 每次实验使用新 ID；这用于练习首次保存，尚不是同 ID 重放。
    raw_payload = scenario["base_request"]
    raw_payload["request_id"] = f"save-demo-{uuid4().hex}"
    payload = RunRequest.model_validate(raw_payload).model_dump()
    payload_hash = hash_payload(payload)
    reordered_fields = dict(reversed(payload.items()))# 方法：取得整个字典的键值对
    assert hash_payload(reordered_fields) == payload_hash
    
    # 将任务排列从 A、B、C 改成 C、B、A，内容发生变化。
    reordered_items={
        **payload,
        "items":list(reversed(payload["items"]))
    }
    assert hash_payload(reordered_items) != payload_hash

    print("摘要规则验证通过")
    # 与导入分开：只有实际运行本实验时才创建表、执行任务和保存。
    init_db()
    with patch.object(
        e03_service,
        "execute_batch",
        wraps= e03_service.execute_batch,
    ) as execute_spy:
        #第一次：数据库没有记录，执行并保存
        result = await e03_service.submit_run(payload)
        assert execute_spy.await_count == 1

        #第二次：相同ID相同内容，直接返回已经保存了的结果
        repeated = await e03_service.submit_run(payload)
        assert repeated == result
        assert execute_spy.await_count == 1

        changed = {**payload, "timeout_ms":70}

        try:
             await e03_service.submit_run(changed)
        except e03_service.RequestConflictError as exc:
            print("冲突验证通过",exc)
        else:
            raise AssertionError("相同ID 内容不同，应该拒绝")
        assert execute_spy.await_count == 1
       

    # 打开新的 Session 读回，核对已经提交的数据。
    with Session(engine) as session:
        record = session.get(RunRecord, payload["request_id"])
        details = session.scalars(
            select(RunItem)
            .where(RunItem.request_id == payload["request_id"])
            .order_by(RunItem.position)
        ).all()

        assert record is not None
        assert record.payload_hash == payload_hash
        assert record.result == result
        assert len(details) == len(payload["items"]) == 3
        assert [
            {"id": row.item_id, "status": row.status, "error_code": row.error_code}
            for row in details
        ] == result["items"]

        print("保存验证通过")
        print("批次 ID：", record.request_id)
        print("本批次主记录：1；任务明细：", len(details))
        print("状态：", record.status, "计数：", record.result["counts"])

    broken = deepcopy(result)
    broken["request_id"] = f"roolback-demo-{uuid4().hex}"
    broken["items"][1]["id"] = None 

    try:
        save_run(broken, payload_hash)
    except IntegrityError as exc:
        print("触发数据库约束异常",exc.orig)
    else:
        raise AssertionError("故障数据应该保存失败")

    #用新会话检查：失败批次的主记录和明细都应不存在。
    with Session(engine) as session:
        record = session.get(RunRecord,broken["request_id"])
        details = session.scalars(
            select(RunItem)
            .where(RunItem.request_id == broken["request_id"])
        ).all()
        assert record is None
        assert details == []
    print("回滚验证通过")
    #故障之后，用新ID提交正常清求。
    recoery_payload = {
        **payload,
        "request_id":f"recovery-demo-{uuid4().hex}",
    }
    recovered = await e03_service.submit_run(recoery_payload)

    #新会话读回，确认结果确定已经提交
    with Session(engine) as session:
        record = session.get(RunRecord,recoery_payload["request_id"])
        assert record is not None
        assert record.result == recovered
    print("恢复验证通过")
    
if __name__ == "__main__":
    asyncio.run(main())
