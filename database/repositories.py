from .database import database
from .models import User
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select


class UserRepository:
    @staticmethod
    async def get_user(telegram_id: int) -> User | None:
        async with database.async_session() as session:
            result = await session.execute(
                select(User).where(User.tg_id == telegram_id)
            )
            return result.scalar_one_or_none()
        
    @staticmethod
    async def create_user(
        telegram_id: int,
        username: str
    ):
        async with database.async_session() as session:
            user = User(
                tg_id=telegram_id,
                username=username
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        
    @staticmethod
    async def update_subscription(telegram_id: int, days: int = 30) -> Optional[User]:
        async with database.async_session as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                now = datetime.now()
                if user.subscription_end and user.subscription_end > now:
                    user.subscription_end += timedelta(days=days)
                else:
                    user.subscription_start = now
                    user.subscription_end = now + timedelta(days=days)
                
                user.has_subscription = True
                await session.commit()
                await session.refresh(user)
            
            return user
        
    async def get_or_create_user(self, telegram_id: int, **kwargs) -> User:
        user = await self.get_user(telegram_id)
        if not user:
            user = await self.create_user(telegram_id, **kwargs)
        return user
    
    async def check_subscription(self, user: User) -> bool:
        if user:
            return user.is_subscription_active()
        return False
    
user_repository = UserRepository()