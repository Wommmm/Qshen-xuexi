"""接收请求。校验失败返回 422,通过后交给执行器。"""
from fastapi import FastAPI,Depends
from e01_models import RunRequest
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from e01_service import FakeExecutor

app=FastAPI()

def get_executor():
    return FakeExecutor()
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/runs")
def create_run(
    body: RunRequest,
    executor:FakeExecutor=Depends(get_executor),
):
    return executor.execute(body)

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
