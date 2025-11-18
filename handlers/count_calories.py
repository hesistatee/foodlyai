from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import UserRepository
from keyboards import main_kb
from services import FoodAnalyzer, ImageProcessor, OpenAIService
from states import MainGroup
from static.texts import OPENAI_SERVICE_ERROR_MESSAGE, PARSE_PRODUCT_TEXT
from utils.decorators import login_required, subscribe_required

router = Router()
image_processor = ImageProcessor()
food_analyzer = FoodAnalyzer(openai_service=OpenAIService())


@router.message(F.text == PARSE_PRODUCT_TEXT)
@login_required
@subscribe_required
async def message_before_count(message: Message, user: User, state: FSMContext):
    await state.set_state(MainGroup.count_the_number_of_calories_state)
    await message.answer("Отправь фото блюда")


@router.message(MainGroup.count_the_number_of_calories_state)
async def count_food_calories(
    message: Message, user: User, session: AsyncSession, state: FSMContext
) -> None:
    if not message.photo:
        await message.answer("Отправьте фото блюда/продукта")
        return
    repo = UserRepository(session=session)

    await repo.update_number_of_requests(user=user)

    status_message = await message.answer("🔍 Анализирую блюдо...")

    base64_image = await image_processor.process_telegram_photo(message=message)
    try:
        response = await food_analyzer.analyze_product_calories(
            base64_image=base64_image
        )
        formatted_response = format_calorie_analysis_response(response)
        await status_message.delete()
        await message.answer(
            formatted_response, parse_mode="HTML", reply_markup=main_kb
        )
    except Exception:
        await status_message.delete()
        await message.answer(OPENAI_SERVICE_ERROR_MESSAGE, parse_mode="HTML")
        await state.clear()

    await state.clear()


def format_calorie_analysis_response(response_data: dict[Any, Any]) -> str:
    """Форматирует ответ анализа калорийности в красивое сообщение"""

    product_name = response_data.get("product_name", "Неизвестный продукт")
    weight = response_data.get("estimated_weight", "N/A")
    calories = response_data.get("calories", "N/A")
    protein = response_data.get("protein", "N/A")
    fat = response_data.get("fat", "N/A")
    carbs = response_data.get("carbs", "N/A")

    message_lines: list[str] = []

    message_lines.append(f"🍽️ <b>{product_name}</b>")
    message_lines.append("")

    message_lines.append("📊 <b>Пищевая ценность:</b>")
    message_lines.append(f"   • Вес: <b>{weight}</b>")
    message_lines.append(f"   • Калории: <b>{calories}</b>")
    message_lines.append("")

    message_lines.append("⚖️ <b>Состав БЖУ:</b>")
    message_lines.append(f"   🥚 Белки: <b>{protein}</b>")
    message_lines.append(f"   🥑 Жиры: <b>{fat}</b>")
    message_lines.append(f"   🌾 Углеводы: <b>{carbs}</b>")
    message_lines.append("")

    description = response_data.get("description", "")
    if description:
        message_lines.append("📝 <b>Дополнительная информация:</b>")
        message_lines.append(f"<i>{description}</i>")
        message_lines.append("")

    return "\n".join(message_lines)
