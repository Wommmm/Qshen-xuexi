"""实验入口：运行本文件，观察合法和非法输入的校验结果。"""

from pydantic import ValidationError

from e01_models import ExecutionOptions, TaskItem, RunRequest


cases=[
    {"max_concurrency":2,"timeout_ms":60,"delay_ms":100},
    {"max_concurrency":0,"timeout_ms":-1,"delay_ms":1000},
    {"max_concurrency":"2","timeout_ms":5000,"delay_ms":-1},
    {"max_concurrency":True,"timeout_ms":5000,"delay_ms":1000},
    {"max_concurrency":2,"timeout_ms":5000,"delay_ms":1000,"debug":True},
]
print("一、字段校验实验")

for data in cases:
    try:
        options=ExecutionOptions.model_validate(data)
        print("通过",options.model_dump())
    except ValidationError as e:
        print("错误：",e.errors())

print("二、单个任务：去除 ID 首尾空格")
item = TaskItem(id=" A ", delay_ms=20, mode="ok")
print("任务：", item.model_dump())

print("三、批次：去空格后重复的 ID 应被拒绝")
try:
    batch = RunRequest(
        request_id=" batch-001 ",
        items=[
            {"id": "A", "delay_ms": 20, "mode": "ok"},
            {"id": " A ", "delay_ms": 30, "mode": "ok"},
        ],
        max_concurrency=2,
        timeout_ms=60,
    )
    print("批次：", batch.model_dump())
except ValidationError as e:
    print("批次被拒绝：", e.errors())

print("结束")
