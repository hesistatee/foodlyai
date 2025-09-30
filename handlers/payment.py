from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from utils.keyboards import get_tariffs_keyboard, choose_analyze_kb
import logging
from database.repositories import UserRepository, TariffRepository, OrderRepository, OrderStatus
from database.models import PaymentMethod
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.in_(["choose_tariff", "extend"]))
async def choose_tariff(callback: CallbackQuery, session: AsyncSession) -> None:
    logger.info(f"Received callback: {callback.data} from user: {callback.from_user.id}")
    
    tg_id = callback.from_user.id
    repo = UserRepository(session=session)
    
    user = await repo.get_user(telegram_id=tg_id)
    
    if not user:
        logger.warning(f"User {tg_id} not found in database")
        await callback.message.answer(
            "👋 Привет! Кажется, мы еще не знакомы.\n"
            "Для начала работы воспользуйтесь командой /start"
        )
        return
    
    logger.info(f"User {tg_id} found, showing tariffs")
    await callback.message.answer("Выбери тариф", reply_markup=await get_tariffs_keyboard(session=session))
    
@router.callback_query(F.data.startswith("tariff_"))
async def handle_tariff_selection(callback: CallbackQuery, session: AsyncSession):
    logger.info(f"Tariff selection callback: {callback.data} from user: {callback.from_user.id}")
    
    tariff_id = callback.data.split("_")[1]
    tg_id = callback.from_user.id
    order_repo = OrderRepository(session=session)
    tariff_repo = TariffRepository(session=session)
    
    logger.debug(f"Getting tariff with ID: {tariff_id}")
    tariff = await tariff_repo.get_tariff(tariff_id=tariff_id)
    
    if not tariff:
        logger.error(f"Tariff {tariff_id} not found")
        await callback.message.answer("Тарифы временно недоступны")
        return
    
    logger.info(f"Creating order for user {tg_id}, tariff {tariff_id}, amount {tariff.price}")
    order = await order_repo.create_order(
        user_id=tg_id,
        tariff_id=tariff.id,
        amount=tariff.price,
        payment_method=PaymentMethod.YOOKASSA
    )
    
    prices = [LabeledPrice(label="Оплата", amount=tariff.price * 100)]
    
    logger.info(f"Sending invoice for order {order.id}")
    await callback.message.answer_invoice(
        title=tariff.name,
        description=tariff.description,
        prices=prices,
        provider_token=settings.YOOKASSA_PAYMENT_TOKEN,
        payload=str(order.id),
        currency="RUB",
    )
    
@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, session: AsyncSession):
    logger.info(f"Pre-checkout query from user {pre_checkout_query.from_user.id}, amount: {pre_checkout_query.total_amount}")
    await pre_checkout_query.answer(ok=True)
        
@router.message(F.successful_payment)
async def successful_payment(message: Message, session: AsyncSession):
    logger.info(f"Successful payment from user {message.from_user.id}")
    
    successful_payment = message.successful_payment
    try:
        order_id = int(successful_payment.invoice_payload)
        logger.info(f"Processing successful payment for order {order_id}")
    except (ValueError, AttributeError) as e:
        logger.error(f"Error parsing invoice payload: {e}, payload: {getattr(successful_payment, 'invoice_payload', 'None')}")
        await message.answer("❌ Ошибка при обработке оплаты")
        return
    
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
        logger.info(f"Order {order_id} updated to COMPLETED")
        user = await user_repo.get_user(telegram_id=message.from_user.id)
        tariff = await tariff_repo.get_tariff(tariff_id=order.tariff_id)
        
        if user and tariff:
            await user_repo.update_subscription(telegram_id=message.from_user.id, days=tariff.days)
            logger.info(f"Subscription updated for user {message.from_user.id}, added {tariff.days} days")
            
            await message.answer(
                f"✅ Оплата прошла успешно!\n"
                f"🎉 Ваша подписка активирована на {tariff.days} дней\n",
                reply_markup=choose_analyze_kb
            )
        else:
            logger.error(f"User {message.from_user.id} or tariff {order.tariff_id} not found after payment")
            await message.answer("❌ Ошибка при активации подписки")
    else:
        logger.error(f"Order {order_id} not found for successful payment")
        await message.answer("❌ Ошибка при обработке оплаты")
        
@router.message(F.content_type == 'unsuccessful_payment')
async def unsuccessful_payment(message: Message, session: AsyncSession):
    logger.warning(f"Unsuccessful payment from user {message.from_user.id}")
    
    try:
        order_id = int(message.successful_payment.invoice_payload)
        logger.info(f"Processing unsuccessful payment for order {order_id}")
    except (ValueError, AttributeError) as e:
        logger.error(f"Error parsing invoice payload for unsuccessful payment: {e}")
        await message.answer("❌ Ошибка при обработке информации об оплате")
        return
    
    order_repo = OrderRepository(session)
    await order_repo.update_order_status(
        order_id=order_id,
        status=OrderStatus.FAILED
    )
    
    logger.info(f"Order {order_id} updated to FAILED")
    await message.answer("❌ Оплата не прошла. Попробуйте еще раз или обратитесь в поддержку")