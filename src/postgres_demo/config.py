from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Settings:
    host: str
    port: int
    database: str
    user: str
    password: str
    sslmode: str = "prefer"
    min_pool_size: int = 1
    max_pool_size: int = 4
    connect_timeout: int = 5
    log_level: str = "INFO"

    @property
    def dsn(self) -> str:
        return (
            f"host={self.host} port={self.port} dbname={self.database} "
            f"user={self.user} password={self.password} sslmode={self.sslmode} "
            f"connect_timeout={self.connect_timeout}"
        )

    @property
    def safe_summary(self) -> str:
        return (
            f"host={self.host} port={self.port} db={self.database} "
            f"user={self.user} sslmode={self.sslmode} "
            f"pool={self.min_pool_size}-{self.max_pool_size} "
            f"connect_timeout={self.connect_timeout}"
        )


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        msg = f"Missing required environment variable: {name}"
        raise ValueError(msg)
    return value


def load_settings() -> Settings:
    min_pool_size = int(os.getenv("POSTGRES_MIN_POOL_SIZE", "1"))
    max_pool_size = int(os.getenv("POSTGRES_MAX_POOL_SIZE", "4"))
    connect_timeout = int(os.getenv("POSTGRES_CONNECT_TIMEOUT", "5"))

    if min_pool_size < 1:
        raise ValueError("POSTGRES_MIN_POOL_SIZE must be at least 1")
    if max_pool_size < min_pool_size:
        raise ValueError(
            "POSTGRES_MAX_POOL_SIZE must be greater than or equal to "
            "POSTGRES_MIN_POOL_SIZE"
        )
    if connect_timeout < 1:
        raise ValueError("POSTGRES_CONNECT_TIMEOUT must be at least 1")

    settings = Settings(
        host=_require_env("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=_require_env("POSTGRES_DB"),
        user=_require_env("POSTGRES_USER"),
        password=_require_env("POSTGRES_PASSWORD"),
        sslmode=os.getenv("POSTGRES_SSLMODE", "prefer"),
        min_pool_size=min_pool_size,
        max_pool_size=max_pool_size,
        connect_timeout=connect_timeout,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
    LOGGER.debug("Loaded settings: %s", settings.safe_summary)
    return settings
