from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def menu_keyboard(lang: str = 'uz') -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(
        KeyboardButton(text="🧠 ChatGPT (OpenAI)"),
        KeyboardButton(text="🔮 Gemini (Google)"),
        KeyboardButton(text="🚀 DeepSeek AI"),
    )
    builder.adjust(2, 1)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
