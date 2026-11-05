"""模型定义：包含早期练习模型和正式请求模型，导入时不会运行实验。"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


# 可复用的 ID 规则：先去首尾空格，再检查长度。
CleanId = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=64,
    ),
]


class ExecutionOptions(BaseModel):
    """早期字段校验练习使用，不作为正式批次请求结构。"""

    model_config = ConfigDict(extra="forbid")

    max_concurrency: int = Field(strict=True, ge=1, le=4)
    delay_ms: int = Field(strict=True, ge=0, le=10000)
    timeout_ms: int = Field(strict=True, ge=10, le=5000)


class TaskItem(BaseModel):
    """单个任务：任务 ID、模拟执行延迟、执行模式。"""

    model_config = ConfigDict(extra="forbid")

    id: CleanId
    delay_ms: int = Field(strict=True, ge=0, le=10000)
    mode: Literal["ok", "error"]


class RunRequest(BaseModel):
    """整个批次：包含任务列表和批次级执行参数。"""

    model_config = ConfigDict(extra="forbid")

    items: list[TaskItem] = Field(min_length=1, max_length=20)
    request_id: CleanId
    max_concurrency: int = Field(strict=True, ge=1, le=4)
    timeout_ms: int = Field(strict=True, ge=10, le=5000)


    @model_validator(mode="after")#先对模型进行校验，再调用次方法
    def check_unique_ids(self):
        # 此时字段已完成校验，item.id 已去除首尾空格。
        ids = [item.id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("id重复")
        return self
