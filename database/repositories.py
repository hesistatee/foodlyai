from .models import User, Tariff, Order, OrderStatus
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class IRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

class UserRepository(IRepository):
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
    
class TariffRepository(IRepository):
    async def get_tariff(self, tariff_id: int) -> Optional[Tariff]:
        result = await self.session.execute(
            select(Tariff).where(Tariff.id == tariff_id)
        )
        return result.scalar_one_or_none()
    
class OrderRepository(IRepository):
    async def get_order(self, order_id: int) -> Optional[Order]:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def create_order(
        self,
        user_id: int,
        tariff_id: int,
        payment_method: str,
        amount: int
    ) -> Optional[Order]:
        order = Order(
            user_id=user_id,
            tariff_id=tariff_id,
            payment_method=payment_method,
            amount=amount
        )
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order
    
    async def update_order_status(
        self, 
        order_id: int, 
        status: OrderStatus,
        payment_id: str = None,
        payment_details: str = None
    ) -> Optional[Order]:
        order = await self.get_order(order_id)
        if order:
            order.status = status
            if payment_id:
                order.payment_id = payment_id
            if payment_details:
                order.payment_details = payment_details
            if status == OrderStatus.COMPLETED:
                order.completed_at = datetime.now()
            self.session.commit()
        return order
        