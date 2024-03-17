from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Функция, создающая клавиатуру с кнопками в одну строку.

    Args:
        items (list[str]): Список элементов для кнопок клавиатуры.

    Returns:
        ReplyKeyboardMarkup: Объект с настройками и разметкой клавиатуры.
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)
