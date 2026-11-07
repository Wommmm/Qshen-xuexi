"""E04 测试准备：每个测试使用独立的临时 SQLite 数据库。"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event

# E03 目前使用同目录导入；让测试能找到这些现有模块。
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "E03"))

import e03_repository
from e03_api import app
from e03_models import Base


@pytest.fixture
def db_engine(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'runs.db'}")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, connection_record):
        cursor = connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    try:
        Base.metadata.create_all(engine)
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def client(db_engine, monkeypatch):
    # 替换仓储实际使用的 engine，避免写入 E03/runs.db。
    monkeypatch.setattr(e03_repository, "engine", db_engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def payload():
    # 每个测试得到一个全新的字典，修改不影响其他测试。
    return {
        "request_id": "e04-001",
        "items": [{"id": "A", "delay_ms": 0, "mode": "ok"}],
        "max_concurrency": 1,
        "timeout_ms": 5000,
    }


