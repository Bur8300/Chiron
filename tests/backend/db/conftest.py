import asyncio
import os
import uuid
from collections.abc import Iterator
from pathlib import Path

import asyncpg
import pytest
from alembic.config import Config
from sqlalchemy.engine import make_url

BACKEND_DIR = Path(__file__).resolve().parents[3] / "backend"


def _admin_dsn() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url and os.environ.get("CI"):
        # In CI a missing DATABASE_URL is a broken workflow. Fail instead of a silent skip.
        pytest.fail("DATABASE_URL is not set in CI. The database tests must run in CI.")
    if not url:
        pytest.skip(
            "DATABASE_URL is not set. Start infra/docker-compose.yml to run database tests."
        )
    return url


def _asyncpg_dsn(url: str) -> str:
    return make_url(url).set(drivername="postgresql").render_as_string(hide_password=False)


@pytest.fixture
def database_url() -> Iterator[str]:
    """Create an empty database for one test and drop it after the test."""
    admin_url = _admin_dsn()
    name = f"chiron_test_{uuid.uuid4().hex[:12]}"

    async def execute(sql: str) -> None:
        connection = await asyncpg.connect(_asyncpg_dsn(admin_url))
        try:
            await connection.execute(sql)
        finally:
            await connection.close()

    asyncio.run(execute(f'CREATE DATABASE "{name}"'))
    try:
        yield make_url(admin_url).set(database=name).render_as_string(hide_password=False)
    finally:
        asyncio.run(execute(f'DROP DATABASE "{name}" WITH (FORCE)'))


@pytest.fixture
def alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


@pytest.fixture
def sql(database_url: str):
    """Run SQL statements on the test database. Returns the rows of the last SELECT."""
    dsn = _asyncpg_dsn(database_url)

    def run(*statements: str) -> list[asyncpg.Record]:
        async def go() -> list[asyncpg.Record]:
            connection = await asyncpg.connect(dsn)
            try:
                rows: list[asyncpg.Record] = []
                for statement in statements:
                    if statement.lstrip().upper().startswith("SELECT"):
                        rows = await connection.fetch(statement)
                    else:
                        await connection.execute(statement)
                return rows
            finally:
                await connection.close()

        return asyncio.run(go())

    return run
