from fastapi import FastAPI
from pydantic import BaseModel,Field

app = FastAPI()


class SearchRequest(BaseModel):
    query: str=Field(min_length=1)
    top_k: int=Field(default=3,ge=1,le=10)


@app.post("/search")
def search(request: SearchRequest):
    return {"query": request.query, "message": "收到检索请求","top_k": request.top_k}