import asyncio
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.bootstrap as bootstrap
from app.core.config import get_settings
from app.main import app


def _dispose_runtime_registry() -> None:
    registry = bootstrap.runtime_registry
    if registry is None:
        return

    asyncio.run(registry.database.engine.dispose())
    bootstrap.reset_runtime_registry()


def _prepare_sqlite_path(sqlite_path: Path) -> None:
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ("", "-shm", "-wal"):
        candidate = Path(f"{sqlite_path}{suffix}")
        if candidate.exists():
            candidate.unlink()


@pytest.fixture
def sqlite_db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    sqlite_path = tmp_path / "test.db"
    _dispose_runtime_registry()
    _prepare_sqlite_path(sqlite_path)

    monkeypatch.setenv("MARP_ENV", "test-local")
    monkeypatch.setenv("MARP_DATABASE_URL", f"sqlite+aiosqlite:///{sqlite_path.as_posix()}")
    monkeypatch.setenv("MARP_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("MARP_DB_AUTO_CREATE_SCHEMA", "true")
    get_settings.cache_clear()

    return sqlite_path


@pytest.fixture
def client(sqlite_db_path: Path) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client

    _dispose_runtime_registry()
    get_settings.cache_clear()


@pytest.fixture
def client_factory(sqlite_db_path: Path) -> Iterator:
    def make_client(*, reset_db: bool) -> TestClient:
        _dispose_runtime_registry()
        if reset_db:
            _prepare_sqlite_path(sqlite_db_path)
        get_settings.cache_clear()
        return TestClient(app)

    yield make_client

    _dispose_runtime_registry()
    get_settings.cache_clear()
