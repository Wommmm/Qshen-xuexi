from fastapi.testclient import TestClient
from copy import deepcopy
from e01_api import app,get_executor
from e01_service import FakeExecutor

def test_inalid_request_does_not_execute():
    fake = FakeExecutor()

    def provide_fake():
        return fake

    app.dependency_overrides[get_executor] = provide_fake

    try:
        with TestClient(app) as client:
            data = {
                "request_id": "test-001",
                "items": [
                    {"id": "A", "delay_ms": 20, "mode": "ok"}
                ],
                "max_concurrency": 2,
                "timeout_ms": 60,
            }
            response = client.post("/runs",json=data)
            assert response.status_code == 200
            assert fake.calls == 1

            result = response.json()

            assert result["request_id"] == "test-001"
            assert result["status"] == "success"
            assert result["items"] == [
                {"id": "A", "status": "success", "error_code": None}
            ]

            assert result["counts"] == {
                "success": 1,
                "error": 0,
                "timeout": 0,
            }

            assert result["metrics"]["latency_ms"] >= 0
            assert result["metrics"]["peak_active"] == 0

            invalid_values = [
                ("request_id", "   "),
                ("items", []),
                ("max_concurrency", "2"),
                ("debug", True),
            ]

            for field, value in invalid_values:
                candidate = deepcopy(data)
                candidate[field] = value

                response = client.post("/runs", json=candidate)

                assert response.status_code == 422
                assert response.json()["error"]["code"] == "invalid_request"
                assert fake.calls == 1

            candidate = deepcopy(data)   
            candidate["items"][0]["mode"] = "unknown" 

            response = client.post("/runs",json=candidate)
            
            assert response.status_code == 422
            assert response.json()["error"]["code"] == "invalid_request"
            assert fake.calls == 1

            

            data["max_concurrency"] = 0
            response = client.post("/runs",json=data)
            assert response.status_code == 422
            assert fake.calls == 1

            data["max_concurrency"] = 2

            data["items"]=[
                {"id": "A", "delay_ms": 20, "mode": "ok"},
                {"id": " A ", "delay_ms": 30, "mode": "ok"}
            ]

            response = client.post("/runs",json=data)

            assert response.status_code == 422
            assert response.json()["error"]["code"] == "invalid_request"
            assert fake.calls == 1

    finally:
        app.dependency_overrides.pop(get_executor,None)        