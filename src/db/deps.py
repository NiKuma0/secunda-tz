import typing

import fastapi
import sqlalchemy.ext.asyncio as sa_async

from src.settings import settings

engine = sa_async.create_async_engine(str(settings.POSTGRES_DSN))
sessionmaker = sa_async.async_sessionmaker(engine)


async def get_session():
    async with sessionmaker() as session:
        yield session
        await session.commit()


SessionDep = typing.Annotated[sa_async.AsyncSession, fastapi.Depends(get_session)]
