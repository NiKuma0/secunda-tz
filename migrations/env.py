import logging
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic_utils.replaceable_entity import register_entities
from alembic import context

from src.db import models, functions, triggers
from src.settings import settings

target_metadata = models.Base.metadata
ENTITIES = (
    functions.check_specialization_depth,
    triggers.trg_specialization_depth_check,
    functions.ensure_org_has_building,
    triggers.trg_ensure_org_has_building,
    triggers.trg_building_update_search_vector,
    triggers.trg_organizations_update_search_vector,
)
ENTITIES_NAMES = {entity.to_variable_name() for entity in ENTITIES}
ENTITIES_TYPES = {'trigger', 'function'}
ALWAYS_ALLOWED = {'column', 'index'}

register_entities(ENTITIES)


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option('sqlalchemy.url', str(settings.POSTGRES_DSN))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    logger = logging.getLogger('alembic.runtime.migration')

    def checker(name: str | None, type_: str, _):
        res: bool
        match type_:
            case 'table':
                res = name in target_metadata.tables
            case _ if type_ in ENTITIES_TYPES:
                res = name in ENTITIES_NAMES
            case _ if type_ in ALWAYS_ALLOWED:
                res = True
            case _:
                res = False
        if res: 
            logger.info("%s, %s", name, type_)
        return res

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_name=checker
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
