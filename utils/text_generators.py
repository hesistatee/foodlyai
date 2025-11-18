from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import FoodRepository


async def get_progress_text(
    session: AsyncSession, user: User, selected_date: date = date.today()
) -> str | None:
    food_repo = FoodRepository(session=session)

    daily_calories = await food_repo.get_user_eat_calories_for_date(
        user_id=user.id, selected_date=selected_date
    )
    weekly_calories = await food_repo.get_user_eat_calories_for_week(
        user_id=user.id, selected_date=selected_date
    )
    day_calories_goal = user.fitness_profile.calorie_norm_for_weight_loss
    week_calories_goal = user.fitness_profile.calorie_norm_for_weight_loss * 7

    text = f"""
        Ваш прогресс за {selected_date.strftime("%d.%m.%Y")}:
        🍽️ Съедено калорий: {daily_calories if daily_calories else 0} / {day_calories_goal} ккал

📊 За неделю:
        🍽️ Съедено калорий: {weekly_calories if weekly_calories else 0} / {week_calories_goal} ккал
        """

    return text


async def get_food_history_text(
    session: AsyncSession, user: User, selected_date: date = date.today()
) -> str | None:
    food_repo = FoodRepository(session=session)

    foods = await food_repo.get_users_food_for_day(
        user_id=user.id, selected_date=selected_date
    )
    if foods:
        text = f"Ваша съединая еда за {selected_date.strftime('%d.%m.%Y')}:"
    else:
        text = f"{selected_date.strftime('%d.%m.%Y')} вы ничего не ели"

    for food in foods:
        text += f"""
            Название: {food.name}
            Ккал: {food.calories}
            Белки: {food.protein}
            Жиры: {food.carbs}
            Углеводы: {food.fat}
            
        """

    return text
