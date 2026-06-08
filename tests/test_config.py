from __future__ import annotations

import os

import pytest

from postgres_demo.config import load_settings


@pytest.fixture(autouse=True)
def clear_env() -> None:
    keys = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_SSLMODE",
        "POSTGRES_MIN_POOL_SIZE",
        "POSTGRES_MAX_POOL_SIZE",
    ]
    for key in keys:
        os.environ.pop(key, None)


def test_load_settings_reads_required_values() -> None:
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_DB"] = "app"
    os.environ["POSTGRES_USER"] = "app_user"
    os.environ["POSTGRES_PASSWORD"] = "secret"

    settings = load_settings()

    assert settings.host == "localhost"
    assert settings.port == 5432
    assert settings.database == "app"
    assert settings.user == "app_user"
    assert settings.password == "secret"
    assert settings.min_pool_size == 1
    assert settings.max_pool_size == 4


def test_load_settings_rejects_invalid_pool_sizes() -> None:
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_DB"] = "app"
    os.environ["POSTGRES_USER"] = "app_user"
    os.environ["POSTGRES_PASSWORD"] = "secret"
    os.environ["POSTGRES_MIN_POOL_SIZE"] = "4"
    os.environ["POSTGRES_MAX_POOL_SIZE"] = "2"

    with pytest.raises(ValueError, match="POSTGRES_MAX_POOL_SIZE"):
        load_settings()
