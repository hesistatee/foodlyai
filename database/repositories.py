from .models import User
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по telegram_id"""
        result = await self.session.execute(
            select(User).where(User.tg_id == telegram_id)
        )
        return result.scalar_one_or_none()
        
    async def create_user(self, telegram_id: int, username: str) -> User:
        """Создать нового пользователя"""
        user = User(
            tg_id=telegram_id,
            username=username
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
        
    async def get_or_create_user(self, telegram_id: int, username: str) -> User:
        """Получить или создать пользователя"""
        create = False
        user = await self.get_user(telegram_id)
        if not user:
            user = await self.create_user(telegram_id, username)
            create = True
        return user, create
        
    async def update_subscription(self, telegram_id: int, days: int) -> Optional[User]:
        """Обновить подписку пользователя"""
        user = await self.get_user(telegram_id)
        
        if user:
            now = datetime.now()
            if user.subscription_end and user.subscription_end > now:
                user.subscription_end += timedelta(days=days)
            else:
                user.subscription_start = now
                user.subscription_end = now + timedelta(days=days)
            
            user.has_subscription = True
            await self.session.commit()
            await self.session.refresh(user)
        
        return user
        
    async def update_number_of_requests(self, telegram_id: int) -> Optional[User]:
        """Увеличить счетчик запросов"""
        user = await self.get_user(telegram_id)
        
        if user:
            user.number_of_requests += 1
            await self.session.commit()
            await self.session.refresh(user)
        
        return user
    
    async def check_subscription_active(self, telegram_id: int) -> bool:
        """Проверить активна ли подписка"""
        user = await self.get_user(telegram_id)
        if user:
            return user.is_subscription_active()
        return False