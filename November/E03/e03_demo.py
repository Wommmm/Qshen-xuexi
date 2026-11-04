# 完整保存实验：复用 E01 校验、E02 执行，调用 E03 保存并读回核对。
import asyncio
import json
from pathlib import Path
from uuid import uuid4

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

    # 与导入分开：只有实际运行本实验时才创建表、执行任务和保存。
    init_db()
    result = await execute_batch(**payload)
    save_run(result, payload_hash)

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

if __name__ == "__main__":
    asyncio.run(main())
