from datetime import date, datetime, timedelta
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import (
    FitnessProfile,
    Food,
    Order,
    OrderStatus,
    PaymentMethod,
    Tariff,
    User,
)


class IRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session


class UserRepository(IRepository):
    async def get_user(self, telegram_id: int | None = None) -> User | None:
        """Получить пользователя по telegram_id"""
        result = await self.session.execute(
            select(User)
            .where(User.tg_id == telegram_id)
            .options(selectinload(User.fitness_profile))
        )
        return result.scalar_one_or_none()

    async def create_user(self, telegram_id: int, username: str | None) -> User:
        """Создать нового пользователя"""
        user = User(tg_id=telegram_id, username=username)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create_user(
        self, telegram_id: int, username: str | None
    ) -> tuple[User, bool]:
        """Получить или создать пользователя"""
        create = False
        user = await self.get_user(telegram_id)
        if not user:
            user = await self.create_user(telegram_id, username)
            create = True
        return user, create

    async def update_subscription(self, user: User, days: int) -> User | None:
        """Обновить подписку пользователя"""
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

    async def update_number_of_requests(self, user: User) -> User | None:
        """Увеличить счетчик запросов"""

        if user:
            user.number_of_requests += 1
            await self.session.commit()
            await self.session.refresh(user)

        return user

    async def check_subscription_active(self, telegram_id: int | None = None) -> bool:
        """Проверить активна ли подписка"""
        user = await self.get_user(telegram_id)
        if user:
            if not user.has_subscription:
                return False
            elif user.has_subscription and (datetime.now() > user.subscription_end):
                user.has_subscription = False
                await self.session.commit()
                await self.session.refresh(user)
                return False
            return datetime.now() < user.subscription_end
        return False


class FitnessProfileRepository(IRepository):
    async def get_fitness_profile(self, user_id: int) -> FitnessProfile | None:
        result = await self.session.execute(
            select(FitnessProfile).where(FitnessProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_fitness_profile(
        self,
        user_id: int,
        current_weight: int,
        desired_weight: int,
        height: int,
        age: int,
        gender: str,
    ) -> FitnessProfile | None:
        fitness_profile = FitnessProfile(
            user_id=user_id,
            current_weight=current_weight,
            desired_weight=desired_weight,
            height=height,
            age=age,
            gender=gender,
        )
        self.session.add(fitness_profile)
        await self.session.commit()
        await self.session.refresh(fitness_profile)
        return fitness_profile


class FoodRepository(IRepository):
    async def get_food(self, food_id: int) -> Food | None:
        result = await self.session.execute(select(Food).where(Food.id == food_id))
        return result.scalar_one_or_none()

    async def create_food(
        self, name: str, calories: float, protein: float, carbs: float, fat: float
    ) -> Food:
        food = Food(name=name, calories=calories, protein=protein, carbs=carbs, fat=fat)
        self.session.add(food)
        await self.session.commit()
        await self.session.refresh(food)
        return food

    async def get_users_food_for_day(
        self, user_id: int, selected_date: date
    ) -> Sequence[Food]:
        result = await self.session.execute(
            select(Food).where(
                Food.user_id == user_id,
                Food.last_eaten_at == selected_date,
            )
        )
        return result.scalars().all()

    async def get_users_food_for_last_week(self, user_id: int) -> Sequence[Food]:
        result = await self.session.execute(
            select(Food).where(
                Food.user_id == user_id,
                Food.last_eaten_at > datetime.now() - timedelta(days=7),
            )
        )
        return result.scalars().all()

    async def get_user_eat_calories_for_date(
        self, user_id: int, selected_date: date
    ) -> int | None:
        result = await self.session.execute(
            select(func.sum(Food.calories)).where(
                Food.user_id == user_id,
                Food.last_eaten_at == selected_date,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_eat_calories_for_week(
        self, user_id: int, selected_date: date
    ) -> int | None:
        result = await self.session.execute(
            select(func.sum(Food.calories)).where(
                Food.user_id == user_id,
                Food.last_eaten_at > date.today() - timedelta(days=7),
            )
        )
        return result.scalar_one_or_none()


class TariffRepository(IRepository):
    async def get_tariff(self, tariff_id: int) -> Tariff | None:
        result = await self.session.execute(
            select(Tariff).where(Tariff.id == tariff_id)
        )
        return result.scalar_one_or_none()


class OrderRepository(IRepository):
    async def get_order(self, order_id: int) -> Order | None:
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def create_order(
        self, user_id: int, tariff_id: int, payment_method: PaymentMethod, amount: float
    ) -> Order | None:
        order = Order(
            user_id=user_id,
            tariff_id=tariff_id,
            payment_method=payment_method,
            amount=amount,
        )
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def update_order_status(
        self,
        order_id: int,
        status: OrderStatus,
        payment_id: str | None = None,
        payment_details: str | None = None,
    ) -> Order | None:
        order = await self.get_order(order_id)
        if order:
            order.status = status
            if payment_id:
                order.payment_id = payment_id
            if payment_details:
                order.payment_details = payment_details
            if status == OrderStatus.COMPLETED:
                order.completed_at = datetime.now()
            await self.session.commit()
        return order
