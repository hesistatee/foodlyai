from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, SuccessfulPayment
from utils.keyboards import get_tariffs_keyboard, payment_keyboard, choose_analyze_kb
from database.repositories import UserRepository, TariffRepository, OrderRepository, OrderStatus
from database.models import PaymentMethod
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


@router.callback_query(F.data == "choose_tariff" or F.data == "extend")
async def choose_tariff(callback: CallbackQuery, session: AsyncSession) -> None:
    tg_id = callback.from_user.id
    repo = UserRepository(session=session)
    
    user = await repo.get_user(telegram_id=tg_id)
    
    if not user:
        await callback.message.answer(
            "👋 Привет! Кажется, мы еще не знакомы.\n"
            "Для начала работы воспользуйтесь командой /start"
        )
        return
    
    await callback.message.answer("Выбери тариф", reply_markup=await get_tariffs_keyboard(session=session))
    
@router.callback_query(F.data.startswith("tariff_"))
async def handle_tariff_selection(callback: CallbackQuery, session: AsyncSession):
    tariff_id = callback.data.split("_")[1]
    tg_id = callback.from_user.id
    order_repo = OrderRepository(session=session)
    tariff_repo = TariffRepository(session=session)
    tariff = await tariff_repo.get_tariff(tariff_id=tariff_id)
    
    if not tariff:
        await callback.message.answer("Тарифы временно недоступны")
        return
    
    order = await order_repo.create_order(
        user_id=tg_id,
        tariff_id=tariff.id,
        amount=tariff.price,
        payment_method=PaymentMethod.STARS
    )
    
    prices = [LabeledPrice(label="XTR", amount=tariff.price)]
    
    await callback.message.answer_invoice(
        title=tariff.name,
        description=tariff.description,
        prices=prices,
        provider_token="",
        payload=str(order.id),
        currency="XTR",
        reply_markup=payment_keyboard(price=tariff.price)
    )
    
@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, session: AsyncSession):
    await pre_checkout_query.answer(ok=True)
        
@router.message(F.successful_payment)
async def successful_payment(message: Message, session: AsyncSession):
    successful_payment = message.successful_payment
    order_id = int(successful_payment.invoice_payload)
    
    order_repo = OrderRepository(session)
    tariff_repo = TariffRepository(session)
    user_repo = UserRepository(session)
    
    order = await order_repo.update_order_status(
        order_id=order_id,
        status=OrderStatus.COMPLETED,
        payment_id=successful_payment.provider_payment_charge_id,
        payment_details=str(successful_payment)
    )
    
    if order:
        user = await user_repo.get_user(telegram_id=message.from_user.id)
        tariff = await tariff_repo.get_tariff(tariff_id=order.tariff_id)
        
        if user and tariff:
            await user_repo.update_subscription(telegram_id=message.from_user.id, days=tariff.days)
            
            await message.answer(
                f"✅ Оплата прошла успешно!\n"
                f"🎉 Ваша подписка активирована на {tariff.days} дней\n"
                f"💳 Сумма: {successful_payment.total_amount} ⭐️",
                reply_markup=choose_analyze_kb
            )
    else:
        await message.answer("❌ Ошибка при обработке оплаты")
        
@router.message(F.content_type == 'unsuccessful_payment')
async def unsuccessful_payment(message: Message, session: AsyncSession):
    order_id = int(message.invoice_payload)
    
    order_repo = OrderRepository(session)
    await order_repo.update_order_status(
        order_id=order_id,
        status=OrderStatus.FAILED
    )
    
    await message.answer("❌ Оплата не прошла. Попробуйте еще раз или обратитесь в поддержку")
    
    
    
    