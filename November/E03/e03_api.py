from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from November.E01.e01_models import RunRequest
from e03_repository import get_run
from e03_service import submit_run,RequestConflictError

app = FastAPI()

@app.get("/health")
def health():
    return{"status": "ok"}

@app.post("/runs")
async def create_run(body:RunRequest):
    #HTTP接受参数，业务流程由service处理
    return await submit_run(body.model_dump())

@app.get("/runs/{request_id}")
def read_run(request_id:str):
    existing = get_run(request_id)

    if existing is None:
        return JSONResponse(
            status_code=404,
            content={
                "error":{
                    "code":"not_found",
                    "message":"未找到该运行",
                }
            },
        )
    return existing["result"]

@app.exception_handler(RequestValidationError)
async def handle_invalid_request(request,exc):
    return JSONResponse(
        status_code=422,
        content={
        "error": {
            "code": "invalid_request",
            "message": "输入参数不符合要求",
        }
      },
    )

@app.exception_handler(RequestConflictError)
async def handle_conflict(request,exc):
    return JSONResponse(
        status_code=409,
        content={
        "error": {
            "code": "request_conflict",
            "message": str(exc),
        }
      },
    )

@app.exception_handler(SQLAlchemyError)
async def handle_storage_error(request,exc):
    return JSONResponse(
        status_code = 503,
        content = {
            "error":{
                "code":"storage_unavailable",
                "message":"数据库操作失败"
            }
        },
    )