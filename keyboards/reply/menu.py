from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def menu_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(
        KeyboardButton(text="🧠 OpenAI"),
        KeyboardButton(text="🔮 Gemini"),
    )
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
