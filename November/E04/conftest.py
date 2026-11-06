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
def client(tmp_path, monkeypatch):
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
        # 替换仓储实际使用的 engine，避免写入 E03/runs.db。
        monkeypatch.setattr(e03_repository, "engine", engine)
        with TestClient(app) as test_client:
            yield test_client
    finally:
        engine.dispose()
