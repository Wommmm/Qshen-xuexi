"""E04 已有接口覆盖：公共请求复用，同类非法输入集中验证。"""
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

import e03_service


def test_submit_then_get(client, payload):
    created = client.post("/runs", json=payload)
    assert created.status_code == 200
    assert created.json()["status"] == "success"
    queried = client.get(f"/runs/{payload['request_id']}")
    assert queried.status_code == 200
    assert queried.json() == created.json()


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"max_concurrency": 0}, id="below-range"),
        pytest.param({"max_concurrency": True}, id="boolean"),
        pytest.param({"max_concurrency": "2"}, id="numeric-string"),
        pytest.param({"max_concurrency": 5}, id="above-range"),
        pytest.param({"items": [
            {"id": "A", "delay_ms": 0, "mode": "ok"},
            {"id": " A ", "delay_ms": 0, "mode": "ok"},
        ]}, id="duplicate-cleaned-ids"),
    ],
)
def test_invalid_request_does_not_execute(client, payload, changes):
    payload.update(changes)
    with patch.object(e03_service, "execute_batch") as executor:
        response = client.post("/runs", json=payload)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "invalid_request"
        executor.assert_not_called()


def test_missing_run_returns_404(client):
    response = client.get("/runs/not-found")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_repeated_request_does_not_execute_again(client, payload):
    with patch.object(e03_service, "execute_batch", wraps=e03_service.execute_batch) as executor:
        first = client.post("/runs", json=payload)
        second = client.post("/runs", json=payload)
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json() == second.json()
        assert executor.await_count == 1


def test_changed_payload_returns_409(client, payload):
    changed = {**payload, "timeout_ms": 4000}
    with patch.object(e03_service, "execute_batch", wraps=e03_service.execute_batch) as executor:
        first = client.post("/runs", json=payload)
        conflict = client.post("/runs", json=changed)
        queried = client.get(f"/runs/{payload['request_id']}")
        assert first.status_code == 200
        assert conflict.status_code == 409
        assert queried.status_code == 200
        assert executor.await_count == 1
        assert conflict.json()["error"]["code"] == "request_conflict"
        assert queried.json() == first.json()


def test_mixed_results(client, payload):
    payload.update({
        "items": [
            {"id": "A", "delay_ms": 0, "mode": "ok"},
            {"id": "B", "delay_ms": 0, "mode": "error"},
            {"id": "C", "delay_ms": 1000, "mode": "ok"},
        ],
        "max_concurrency": 2,
        "timeout_ms": 100,
    })
    response = client.post("/runs", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "partial"
    assert body["counts"] == {"success": 1, "error": 1, "timeout": 1}
    assert body["items"] == [
        {"id": "A", "status": "success", "error_code": None},
        {"id": "B", "status": "error", "error_code": "worker_failed"},
        {"id": "C", "status": "timeout", "error_code": "worker_timeout"},
    ]


def test_storage_failure_returns_503(client, payload):
    with patch.object(e03_service, "save_run", side_effect=SQLAlchemyError("模拟保存失败")):
        response = client.post("/runs", json=payload)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "storage_unavailable"
