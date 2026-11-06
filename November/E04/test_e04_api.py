"""E04 第一项：通过 HTTP 接口提交，再查询同一结果。"""
from unittest.mock import patch
import e03_service
from sqlalchemy.exc import SQLAlchemyError
import pytest

def test_submit_then_get(client):
    payload = {
        "request_id": "e04-001",
        "items": [{"id": "A", "delay_ms": 0, "mode": "ok"}],
        "max_concurrency": 1,
        "timeout_ms": 5000,
    }


    created = client.post("/runs",json = payload)
    assert created.status_code == 200
    assert created.json()["status"] == "success"
    queried = client.get("/runs/e04-001")
    assert queried.status_code == 200
    assert queried.json() == created.json()

def test_invalid_request_does_not_execute(client):
    payload = {
        "request_id": "invalid-001",
        "items": [{"id": "A", "delay_ms": 0, "mode": "ok"}],
        "max_concurrency": 0,
        "timeout_ms": 5000,
    }

    with patch.object(e03_service, "execute_batch") as executor:
        response = client.post("/runs", json=payload)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "invalid_request"
        executor.assert_not_called()

def test_missing_run_returns_404(client):
    response = client.get("/runs/not-found")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"

def test_repeated_request_does_not_execute_again(client):
    payload={
        "request_id":"repeat-001",
        "items":[{
            "id":"A",
            "delay_ms":1,
            "mode":"ok"
        }],
        "max_concurrency":1,
        "timeout_ms":5000,
    }
    with patch.object(
        e03_service, 
        "execute_batch",
        wraps=e03_service.execute_batch
        ) as executor:
        first = client.post("/runs",json=payload)
        second = client.post("/runs",json=payload)
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json() == second.json()
        assert executor.await_count == 1

def test_changed_payload_returns_409(client):
    payload = {
        "request_id": "conflict-001",
        "items": [
            {"id": "A","delay_ms":0,"mode":"ok"}
        ],
        "max_concurrency": 1,
        "timeout_ms": 5000,
    }
    changed = {**payload,"timeout_ms": 4000}

    with patch.object(
        e03_service,
        "execute_batch",
        wraps= e03_service.execute_batch,
    ) as executor:
        first = client.post("/runs", json=payload)
        conflict = client.post("/runs", json=changed)
        queried = client.get("/runs/conflict-001")
        assert first.status_code == 200
        assert conflict.status_code == 409
        assert queried.status_code == 200
        assert executor.await_count == 1
        assert conflict.json()["error"]["code"] == "request_conflict"
        assert queried.json() == first.json()

def test_mixed_results(client):
    payload = {
            "request_id": "mixed-001",
        "items": [
            {"id": "A", "delay_ms": 0, "mode": "ok"},
            {"id": "B", "delay_ms": 0, "mode": "error"},
            {"id": "C", "delay_ms": 1000, "mode": "ok"},
        ],
        "max_concurrency": 2,
        "timeout_ms": 100,
    }

    response = client.post("/runs",json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "partial"
    assert body["counts"] == {"success": 1, "error": 1, "timeout": 1}
    assert body["items"] == [
        {"id": "A", "status": "success", "error_code": None},
        {"id": "B", "status": "error", "error_code": "worker_failed"},
        {"id": "C", "status": "timeout", "error_code": "worker_timeout"},
    ]

def test_storage_failure_returns_503(client):
    payload = {
        "request_id": "storage-fail-001",
        "items": [{"id": "A", "delay_ms": 0, "mode": "ok"}],
        "max_concurrency": 1,
        "timeout_ms": 5000,
    }

    with patch.object(
        e03_service,
        "save_run",
        side_effect=SQLAlchemyError("模拟保存失败"),
    ):
        response = client.post("/runs", json=payload)

    # 在这里补上断言。
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "storage_unavailable"


@pytest.mark.parametrize("invalid_limit",[True,"2",5])
def test_invalid_concurrency(client,invalid_limit):
    payload = {
        "request_id": "invalid-limit",
        "items": [{"id": "A", "delay_ms": 0, "mode": "ok"}],
        "max_concurrency": invalid_limit,
        "timeout_ms": 5000,
    }
    with patch.object(e03_service, "execute_batch") as executor:
        response = client.post("/runs",json=payload)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "invalid_request"
        executor.assert_not_called()


def test_duplicate_item_ids_are_rejected(client):
    payload = {
        "request_id": "duplicate-001",
        "items": [
            {"id": "A", "delay_ms": 0, "mode": "ok"},
            {"id": " A ", "delay_ms": 0, "mode": "ok"},
        ],
        "max_concurrency": 1,
        "timeout_ms": 5000,
    }

    with patch.object(e03_service, "execute_batch") as executor:
        response = client.post("/runs", json=payload)





