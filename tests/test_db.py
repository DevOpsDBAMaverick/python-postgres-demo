from __future__ import annotations

from postgres_demo.config import Settings
from postgres_demo.db import Database


class FakeCursor:
    def __init__(self, row: dict[str, object]) -> None:
        self._row = row
        self.executed: list[str] = []

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def execute(self, query: str) -> None:
        self.executed.append(query)

    def fetchone(self) -> dict[str, object]:
        return self._row


class FakeConnection:
    def __init__(self, row: dict[str, object]) -> None:
        self._row = row

    def __enter__(self) -> FakeConnection:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def cursor(self) -> FakeCursor:
        return FakeCursor(self._row)


class FakePool:
    def __init__(self, row: dict[str, object]) -> None:
        self._row = row
        self.closed = False

    def connection(self) -> FakeConnection:
        return FakeConnection(self._row)

    def close(self) -> None:
        self.closed = True


def test_healthcheck_returns_query_result() -> None:
    settings = Settings(
        host="localhost",
        port=5432,
        database="app",
        user="app_user",
        password="secret",
    )
    database = Database(settings)
    database._pool = FakePool(
        {
            "database_name": "app",
            "user_name": "app_user",
            "server_version": "PostgreSQL 16",
        }
    )

    result = database.healthcheck()

    assert result["database_name"] == "app"
    assert result["user_name"] == "app_user"


def test_close_resets_pool() -> None:
    settings = Settings(
        host="localhost",
        port=5432,
        database="app",
        user="app_user",
        password="secret",
    )
    fake_pool = FakePool(
        {
            "database_name": "app",
            "user_name": "app_user",
            "server_version": "PostgreSQL 16",
        }
    )
    database = Database(settings)
    database._pool = fake_pool

    database.close()

    assert fake_pool.closed is True
    assert database._pool is None
