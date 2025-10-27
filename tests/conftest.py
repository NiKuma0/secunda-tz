import pytest
import sqlalchemy as sa
from sqlalchemy import engine as sa_engine
from sqlalchemy.ext import asyncio as async_sa

from src.db import models
from src.settings import settings

TEST_DB_NAME = 'test'

test_db_url = sa_engine.make_url(str(settings.POSTGRES_DSN))
test_db_url = test_db_url.set(database=TEST_DB_NAME)


def _main_engine() -> async_sa.AsyncEngine:
    url = test_db_url.set(database='postgres')
    return async_sa.create_async_engine(url, isolation_level='AUTOCOMMIT')


async def create_database() -> None:
    engine = _main_engine()
    async with engine.connect() as conn:
        c = await conn.execute(sa.text(f"SELECT 1 FROM pg_database WHERE datname='{TEST_DB_NAME}'"))  # noqa: S608
        database_exists = c.scalar() == 1

    if database_exists:
        async with engine.connect() as conn:
            await drop_database()

    async with engine.connect() as conn:
        await conn.run_sync(
            lambda conn: conn.execute(sa.text(f'CREATE DATABASE "{TEST_DB_NAME}" ENCODING "utf8" TEMPLATE template1')),
        )
    await engine.dispose()


async def drop_database() -> None:
    engine = _main_engine()
    async with engine.connect() as conn:
        disc_users = """
        SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{database}'
            AND {pid_column} <> pg_backend_pid();
        """.format(  # noqa: S608
            pid_column='pid',
            database=TEST_DB_NAME,
        )
        await conn.execute(sa.text(disc_users))

        await conn.execute(sa.text(f'DROP DATABASE "{TEST_DB_NAME}"'))


@pytest.fixture(scope='session')
async def db():
    await create_database()

    engine = async_sa.create_async_engine(test_db_url)

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda conn: conn.execute(sa.text('CREATE EXTENSION IF NOT EXISTS postgis')),
        )
        await conn.run_sync(models.Base.metadata.create_all)
    await engine.dispose()

    try:
        yield test_db_url
    finally:
        await drop_database()


@pytest.fixture
async def engine(db: str):
    engine = async_sa.create_async_engine(db)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(name='connection')
async def get_connection(engine: async_sa.AsyncEngine) -> async_sa.AsyncConnection:
    return await engine.connect()


@pytest.fixture(name='sessionmaker')
async def get_sessionmaker(connection: async_sa.AsyncConnection) -> async_sa.async_sessionmaker[async_sa.AsyncSession]:
    return async_sa.async_sessionmaker(connection, expire_on_commit=False)


@pytest.fixture
async def session(
    connection: async_sa.AsyncConnection, sessionmaker: async_sa.async_sessionmaker[async_sa.AsyncSession]
):
    trans = await connection.begin()
    session = sessionmaker()
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()
