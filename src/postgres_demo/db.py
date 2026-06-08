from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import cast

from psycopg import Connection, OperationalError, connect
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool, PoolTimeout

from postgres_demo.config import Settings

LOGGER = logging.getLogger(__name__)


class Database:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pool: ConnectionPool | None = None

    def open(self) -> None:
        if self._pool is not None:
            LOGGER.debug("Pool already open")
            return

        LOGGER.info("Opening connection pool")
        LOGGER.debug("Pool settings: %s", self._settings.safe_summary)
        self._pool = ConnectionPool(
            conninfo=self._settings.dsn,
            min_size=self._settings.min_pool_size,
            max_size=self._settings.max_pool_size,
            timeout=float(self._settings.connect_timeout),
            kwargs={"row_factory": dict_row},
            open=True,
        )
        LOGGER.info("Connection pool opened")

    def close(self) -> None:
        if self._pool is None:
            LOGGER.debug("Pool already closed")
            return

        LOGGER.info("Closing connection pool")
        self._pool.close()
        self._pool = None
        LOGGER.info("Connection pool closed")

    @contextmanager
    def connection(self) -> Iterator[Connection[dict[str, object]]]:
        if self._pool is None:
            self.open()
        if self._pool is None:
            raise RuntimeError("Database pool failed to initialize")

        LOGGER.info("Requesting connection from pool")
        try:
            with self._pool.connection() as conn:
                LOGGER.info("Connection acquired from pool")
                yield cast(Connection[dict[str, object]], conn)
        except PoolTimeout:
            LOGGER.exception("Timed out waiting for a pooled connection")
            raise
        except OperationalError:
            LOGGER.exception("Operational error while acquiring pooled connection")
            raise

    def probe_direct_connection(self) -> None:
        LOGGER.info("Probing direct PostgreSQL connection")
        try:
            with (
                connect(
                    self._settings.dsn,
                    row_factory=dict_row,
                ) as conn,
                conn.cursor() as cur,
            ):
                cur.execute("select 1 as ok")
                row = cur.fetchone()
            LOGGER.info("Direct PostgreSQL connection succeeded: %s", row)
        except OperationalError:
            LOGGER.exception("Direct PostgreSQL connection failed")
            raise

    def healthcheck(self) -> dict[str, object]:
        query = (
            "select current_database() as database_name, "
            "current_user as user_name, version() as server_version"
        )
        LOGGER.info("Starting healthcheck query")
        with self.connection() as conn, conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()

        if row is None:
            raise RuntimeError("Healthcheck query returned no rows")

        LOGGER.info("Healthcheck query completed successfully")
        return row
