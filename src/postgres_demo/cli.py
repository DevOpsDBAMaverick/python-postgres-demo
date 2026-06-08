from __future__ import annotations

import logging
import sys

from psycopg import OperationalError
from psycopg_pool import PoolTimeout

from postgres_demo.config import load_settings
from postgres_demo.db import Database


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    logging.getLogger("psycopg.pool").setLevel(logging.INFO)


def main() -> int:
    settings = load_settings()
    configure_logging(settings.log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting postgres demo CLI")
    logger.info("Runtime settings: %s", settings.safe_summary)

    database = Database(settings)

    try:
        database.probe_direct_connection()
        result = database.healthcheck()
        print("Connected to PostgreSQL successfully.")
        print(f"Database: {result['database_name']}")
        print(f"User: {result['user_name']}")
        print(f"Version: {result['server_version']}")
        return 0
    except PoolTimeout:
        logger.exception("Pool timeout while acquiring database connection")
        print(
            "Database pool timeout. Direct connection may work while pool "
            "initialization or acquisition is failing.",
            file=sys.stderr,
        )
        return 1
    except OperationalError:
        logger.exception("Operational database error")
        print(
            "Operational database error. Check credentials, SSL mode, network "
            "path, and RDS accessibility.",
            file=sys.stderr,
        )
        return 1
    finally:
        database.close()


if __name__ == "__main__":
    raise SystemExit(main())
