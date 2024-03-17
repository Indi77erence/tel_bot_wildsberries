import datetime
import uuid
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types

sys.path.append(".")

from src.bot.handlers.handlers import keyboards
from src.bot.keyboards.simple_row import make_row_keyboard
from src.bot.service import get_data_product, save_request, get_last_product
from src.config import bot_token

load_dotenv()

dp = Dispatcher()
bot = Bot(token=bot_token)
subscribed_users = set()  # Множество, хранящее id пользователей, которые подписаны на какой-либо товар.


class MenuStates(StatesGroup):
    """
    Класс-контейнер для определения состояний FSM (finite state machine) бота.

    Attributes:
        choosing_actions (State): Состояние выбора действий пользователем.
        get_product_info (State): Состояние получения информации о товаре.
    """
    choosing_actions = State()
    get_product_info = State()


@dp.message(StateFilter(None), Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработчик команды "/start" для начала взаимодействия с ботом.

    Args:
        message (Message): Объект, представляющий входящее сообщение.
        state (FSMContext): Контекст FSM (finite state machine) для управления состояниями.

    Returns:
        None
    """
    await message.answer(
        text="Выберите вариант взаимодействия:",  # Отправляем пользователю текстовое сообщение
        reply_markup=make_row_keyboard(keyboards)  # Добавляем клавиатуру с вариантами взаимодействия
    )
    await state.set_state(MenuStates.choosing_actions)  # Устанавливаем состояние FSM на "choosing_actions"


@dp.message(MenuStates.choosing_actions)
async def choosing_actions(message: Message, state: FSMContext) -> Message:
    """
    Обработчик состояния FSM "choosing_actions" для выбора действий пользователем.

    Args:
        message (Message): Объект, представляющий входящее сообщение.
        state (FSMContext): Контекст FSM (finite state machine) для управления состояниями.

    Returns:
        Message
    """
    await state.update_data(chosen_actions=message.text.lower())

    if message.text.lower() == "получить информацию по товару":
        await state.set_state(MenuStates.get_product_info)
        await message.answer(
          text="Теперь укажите артикул товара в сообщении для меня.",
          reply_markup=make_row_keyboard(keyboards)
        )

    elif message.text.lower() == "получить информацию из бд":
        products = await get_last_product(message.from_user.id)
        await message.answer(products, reply_markup=make_row_keyboard(keyboards))
        await state.set_state(MenuStates.choosing_actions)

    elif message.text.lower() == "остановить уведомления":
        if message.from_user.id in subscribed_users:
            subscribed_users.remove(message.from_user.id)
            await message.answer("Вы отписались.", reply_markup=make_row_keyboard(keyboards))
        else:
            await message.answer(
                "Вы не подписаны ни на какой из товаров.",
                reply_markup=make_row_keyboard(keyboards)
            )
    else:
        await message.answer(
            text="Я не знаю такой команды",
            reply_markup=make_row_keyboard(keyboards)
        )


@dp.message(MenuStates.get_product_info)
async def get_product_info(message: Message, state: FSMContext) -> Message:
    """
    Обработчик состояния FSM "get_product_info" для получения информации о товаре.

    Args:
        message (Message): Объект, представляющий входящее сообщение.
        state (FSMContext): Контекст FSM (finite state machine) для управления состояниями.

    Returns:
        Message
    """
    try:
        await state.update_data(chosen_actions=message.text.lower())
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Подписаться",
            callback_data="подписаться")
        )
        vendor_code = message.text

        data_request = {"id": uuid.uuid4(), "date_request": datetime.datetime.now(),
                        "user_id": str(message.from_user.id), "vendor_code": vendor_code}

        product = await get_data_product(vendor_code=vendor_code, user_id=message.from_user.id)
        await save_request(data_request)
        await message.answer(product, reply_markup=builder.as_markup())
        await state.set_state(MenuStates.choosing_actions)
    except IndexError:
        await state.set_state(MenuStates.choosing_actions)
        await message.answer("Вы ввели некорректный артикул, попробуйте еще раз)",
                             reply_markup=make_row_keyboard(keyboards))


@dp.callback_query(lambda c: c.data == 'подписаться')
async def handle_subscribe(callback_query: types.CallbackQuery):
    """
    Обработчик колбэка для подписки на уведомления каждые 5 минут.

    Args:
        callback_query (CallbackQuery): Объект, представляющий входящий колбэк.

    Returns:
        None
    """
    await callback_query.answer("Вы подписались на уведомления каждые 5 минут.")
    vendor_code = callback_query.message.text.split("\n")[1].split(" ")[1].strip()
    subscribed_users.add(callback_query.message.chat.id)
    asyncio.create_task(send_data_periodically(callback_query.from_user.id, vendor_code))


async def send_data_periodically(user_id: int, vendor_code: int):
    """
    Асинхронная функция для периодической отправки данных пользователю.

    Args:
        user_id (int): Идентификатор пользователя.
        vendor_code (int): Артикул товара.

    Returns:
        None
    """
    while user_id in subscribed_users:
        product = await get_data_product(vendor_code=vendor_code, user_id=user_id)
        await bot.send_message(user_id, product)
        await asyncio.sleep(300)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
