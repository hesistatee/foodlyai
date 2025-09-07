from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from services.image_processor import ImageProcessor
from services.food_analyzer_service import FoodAnalyzer
from static.texts import COUNT_THE_NUMBER_OF_CALORIES_TEXT
from utils.states import MainGroup
from utils.keyboards import choose_action_kb

router = Router()
image_processor = ImageProcessor()
food_analyzer = FoodAnalyzer()


@router.message(F.text == COUNT_THE_NUMBER_OF_CALORIES_TEXT)
async def message_before_count(message: Message, state: FSMContext):
    await state.set_state(MainGroup.count_the_number_of_calories_state)
    await message.answer("Отправь фото блюда")
    
@router.message(MainGroup.count_the_number_of_calories_state)
async def analyze_food_composition(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer("Отправьте фото блюда/продукта")
        return    
        
    status_message = await message.answer("🔍 Анализирую блюдо...")
    
    base64_image = await image_processor.process_telegram_photo(message=message)
    response = food_analyzer.analyze_product_calories(base64_image=base64_image)
    
    formatted_response = format_calorie_analysis_response(response)
    await status_message.delete()
    
    await message.answer(
        formatted_response,
        parse_mode='HTML',
        reply_markup=choose_action_kb
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