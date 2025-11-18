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
from static.texts import OPENAI_SERVICE_ERROR_MESSAGE, SCAN_PRODUCT_COMPOSITION_TEXT
from utils.decorators import login_required, subscribe_required

router = Router()
image_processor = ImageProcessor()
food_analyzer = FoodAnalyzer(openai_service=OpenAIService())


@router.message(F.text == SCAN_PRODUCT_COMPOSITION_TEXT)
@login_required
@subscribe_required
async def message_before_analyze(message: Message, user: User, state: FSMContext):
    await state.set_state(MainGroup.analyze_product_composition_state)
    await message.answer("Отправь фотографию состава для разбора")


@router.message(MainGroup.analyze_product_composition_state)
async def analyze_food_composition(
    message: Message, user: User, session: AsyncSession, state: FSMContext
) -> None:
    if not message.photo:
        await message.answer("Отправьте фото состава")
        return

    repo = UserRepository(session=session)

    await repo.update_number_of_requests(user=user)

    status_message = await message.answer("🔍 Разбираю состав...")

    base64_image = await image_processor.process_telegram_photo(message=message)
    try:
        response = await food_analyzer.analyze_product_composition(
            base64_image=base64_image
        )
        formatted_response = format_analysis_response(response)
        await status_message.delete()

        await message.answer(
            formatted_response, parse_mode="HTML", reply_markup=main_kb
        )
    except Exception:
        await status_message.delete()
        await message.answer(OPENAI_SERVICE_ERROR_MESSAGE, parse_mode="HTML")
        await state.clear()

    await state.clear()


def format_analysis_response(response_data: dict[Any, Any]) -> str:
    """Форматирует ответ анализа в красивое сообщение"""

    harmful = response_data.get("harmful_substances", [])
    beneficial = response_data.get("beneficial_substances", [])
    score = response_data.get("product_score", 0)
    explanation = response_data.get("explanation", "")

    message_lines: list[str] = []

    message_lines.append(f"<b>🏆 Оценка продукта: {score}/10</b>")
    message_lines.append(f"<i>{explanation}</i>")
    message_lines.append("")

    if harmful:
        message_lines.append("⚠️ <b>Вредные вещества:</b>")
        for substance in harmful:
            message_lines.append(f"• {substance}")
    else:
        message_lines.append("✅ <b>Вредные вещества:</b> не обнаружены")

    message_lines.append("")

    if beneficial:
        message_lines.append("🌿 <b>Полезные вещества:</b>")
        for substance in beneficial:
            message_lines.append(f"• {substance}")
    else:
        message_lines.append("❌ <b>Полезные вещества:</b> не обнаружены")

    message_lines.append("")

    message_lines.append("📊 <b>Шкала качества:</b>")
    message_lines.append(f"[{'⭐' * score}{'☆' * (10 - score)}]")

    return "\n".join(message_lines)
