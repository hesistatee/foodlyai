from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from services.image_processor import ImageProcessor
from services.food_analyzer_service import FoodAnalyzer
from static.texts import COUNT_THE_NUMBER_OF_CALORIES_TEXT, OPENAI_SERVICE_ERROR_MESSAGE
from utils.states import MainGroup
from utils.keyboards import choose_analyze_kb
from database.repositories import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
image_processor = ImageProcessor()
food_analyzer = FoodAnalyzer()


@router.message(F.text == COUNT_THE_NUMBER_OF_CALORIES_TEXT)
async def message_before_count(message: Message, session: AsyncSession, state: FSMContext):
    tg_id = message.from_user.id
    repo = UserRepository(session=session)
    user = await repo.get_user(telegram_id=tg_id)
    
    if not user:
        await message.answer("👋 Привет! Кажется, мы еще не знакомы.\nДля начала работы воспользуйтесь командой /start")
        return
    elif not await repo.check_subscription_active(telegram_id=tg_id) and not user.is_admin:
        await message.answer("⚠️ Ваша подписка завершилась\n\nЧтобы продолжить пользоваться всеми возможностями, пожалуйста, продлите подписку 💫")
        return
        
    await state.set_state(MainGroup.count_the_number_of_calories_state)
    await message.answer("Отправь фото блюда")
    
@router.message(MainGroup.count_the_number_of_calories_state)
async def count_food_calories(message: Message, session: AsyncSession, state: FSMContext) -> None:
    if not message.photo:
        await message.answer("Отправьте фото блюда/продукта")
        return
    repo = UserRepository(session=session)
    
    await repo.update_number_of_requests(telegram_id=message.from_user.id)
        
    status_message = await message.answer("🔍 Анализирую блюдо...")
    
    base64_image = await image_processor.process_telegram_photo(message=message)
    try:
        response = await food_analyzer.analyze_product_calories(base64_image=base64_image)
    except Exception:
        await status_message.delete()
        await message.answer(
            OPENAI_SERVICE_ERROR_MESSAGE,
            parse_mode='HTML'
        )
        await state.clear()
        
    formatted_response = format_calorie_analysis_response(response)
    await status_message.delete()
    
    await message.answer(
        formatted_response,
        parse_mode='HTML',
        reply_markup=choose_analyze_kb
    )
    
    await state.clear()
    
def format_calorie_analysis_response(response_data: dict) -> str:
    """Форматирует ответ анализа калорийности в красивое сообщение"""
    
    product_name = response_data.get('product_name', 'Неизвестный продукт')
    weight = response_data.get('estimated_weight', 'N/A')
    calories = response_data.get('calories', 'N/A')
    protein = response_data.get('protein', 'N/A')
    fat = response_data.get('fat', 'N/A')
    carbs = response_data.get('carbs', 'N/A')
    
    message_lines = []
    
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
    
    description = response_data.get('description', '')
    if description:
        message_lines.append("📝 <b>Дополнительная информация:</b>")
        message_lines.append(f"<i>{description}</i>")
        message_lines.append("")
    
    return "\n".join(message_lines)