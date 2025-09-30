from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .models import Base
from config import settings


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
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False,
            autoflush=False 
        )
    
    async def get_db(self):
        try:
            session: AsyncSession = self.async_session()
            yield session
        finally:
            await session.close()
            
    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    async def drop_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            
            
database = Database()