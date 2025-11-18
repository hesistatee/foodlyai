from typing import final

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings


@final
class Database:
    def __init__(self):
        self.engine = create_async_engine(
            url=settings.DATABASE_URL,
            echo=True,
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
        )

    async def get_db(self):
        session: AsyncSession = self.async_session()
        try:
            yield session
        finally:
            await session.close()


database = Database()
