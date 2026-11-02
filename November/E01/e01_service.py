from e01_models import RunRequest
from time import perf_counter


class FakeExecutor:
    def __init__(self):
        self.calls = 0

    def execute(self, body:RunRequest):
        self.calls += 1  
        start = perf_counter()

        items = [
            {
                "id": item.id,
                "status": "success",
                "error_code":None,
            }
            for item in body.items
        ]

        return {
            "request_id": body.request_id,
            "status": "success",
            "items": items,
            "counts": {
                "success": len(items),
                "error": 0,
                "timeout": 0,
            },
            "metrics": {
                "latency_ms": int((perf_counter() - start) * 1000),
                "peak_active": 0,
            },
        }