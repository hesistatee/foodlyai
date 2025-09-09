from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from services.image_processor import ImageProcessor
from services.food_analyzer_service import FoodAnalyzer
from static.texts import SCAN_PRODUCT_COMPOSITION_TEXT
from database.repositories import UserRepository
from utils.keyboards import choose_action_kb
from utils.states import MainGroup
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
image_processor = ImageProcessor()
food_analyzer = FoodAnalyzer()


@router.message(F.text == SCAN_PRODUCT_COMPOSITION_TEXT)
async def message_before_analyze(message: Message, session: AsyncSession, state: FSMContext) -> None:
    tg_id = message.from_user.id
    repo = UserRepository(session=session)
    user = await repo.get_user(tg_id)
    
    if not user:
        await message.answer("👋 Привет! Кажется, мы еще не знакомы.\nДля начала работы воспользуйтесь командой /start")
        return
    elif not await repo.check_subscription_active(telegram_id=tg_id) and not user.is_admin:
        await message.answer("⚠️ Ваша подписка завершилась\n\nЧтобы продолжить пользоваться всеми возможностями, пожалуйста, продлите подписку 💫")
        return
    
    await state.set_state(MainGroup.analyze_product_composition_state)
    await message.answer("Отправь фотографию состава для разбора")
    

@router.message(MainGroup.analyze_product_composition_state)
async def analyze_food_composition(message: Message, session: AsyncSession, state: FSMContext) -> None:
    if not message.photo:
        await message.answer("Отправьте фото состава")
        return
    
    repo = UserRepository(session=session)
    
    user = await repo.get_user(telegram_id=message.from_user.id)
    user.number_of_requests += 1
        
    status_message = await message.answer("🔍 Разбираю состав...")
    
    base64_image = await image_processor.process_telegram_photo(message=message)
    response = food_analyzer.analyze_product_composition(base64_image=base64_image)
    
    formatted_response = format_analysis_response(response)
    await status_message.delete()
    
    await message.answer(
        formatted_response,
        parse_mode='HTML',
        reply_markup=choose_action_kb
    )
    
    await state.clear()

def format_analysis_response(response_data: dict) -> str:
    """Форматирует ответ анализа в красивое сообщение"""
    
    harmful = response_data.get('harmful_substances', [])
    beneficial = response_data.get('beneficial_substances', [])
    score = response_data.get('product_score', 0)
    explanation = response_data.get('explanation', '')
    
    message_lines = []
    
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