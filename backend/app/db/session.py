"""Database engine and sessions. The URL comes from the DATABASE_URL environment variable."""

import os
from collections.abc import AsyncIterator
from functools import cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@cache
def session_factory() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that gives one session for each request."""
    async with session_factory()() as session:
        yield session
