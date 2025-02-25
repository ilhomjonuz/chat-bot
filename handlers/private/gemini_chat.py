from collections import defaultdict
from functools import wraps

import google.generativeai as ai
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import logging
from datetime import datetime

from data import config
from loader import dp, bot, gemini_data_manager
from states import ChatStates, GeminiAnswering

# Logging sozlash
logger = logging.getLogger(__name__)

# Google Gemini API ni sozlash
ai.configure(api_key=config.GEMINI_API_KEY)
model = ai.GenerativeModel(config.GEMINI_MODEL)


@dp.message(F.text == '🔮 Gemini (Google)')
async def gemini_chat_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)

    # Yangi chat boshlanganda history ni tozalash
    gemini_data_manager.clear_history(user_id)

    text = (
        "Google Gemini AI model orqali javob beriladi!\n"
        "Savolingizni yuboring"
    )
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ChatStates.gemini)


@dp.message(GeminiAnswering.answering)
async def typing_gemini_bot(message: Message):
    await message.reply("⚠️ Iltimos, xabarlar orasida ozgina kutib turing!")


def rate_limit(limit: int = 3, period: int = 60):
    """
    Rate limiting dekoratori
    :param limit: Ruxsat etilgan so‘rovlar soni
    :param period: Vaqt oralig'i (sekundlarda)
    """
    requests = defaultdict(list)

    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            user_id = str(message.from_user.id)
            current_time = datetime.now()

            # Eski so‘rovlarni o‘chirish
            requests[user_id] = [
                req_time for req_time in requests[user_id]
                if (current_time - req_time).seconds < period
            ]

            # So‘rovlar sonini tekshirish
            if len(requests[user_id]) >= limit:
                await message.reply(
                    f"⚠️ Juda ko‘p so‘rov yubordingiz. "
                    f"Iltimos, {period} sekund kutib turing."
                )
                return

            # Yangi so‘rovni qo‘shish
            requests[user_id].append(current_time)

            return await func(message, *args, **kwargs)

        return wrapper

    return decorator


def markdown_to_html(text: str) -> str:
    """Markdown formatini HTML ga o‘zgartirish"""
    # Avval barcha HTML teglarni tozalash
    text = text.replace('<', '&lt;').replace('>', '&gt;')

    # Sarlavhalar
    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        if line.startswith('# '):
            line = f"<b>{line[2:]}</b>"
        elif line.startswith('## '):
            line = f"<b>{line[3:]}</b>"
        processed_lines.append(line)

    text = '\n'.join(processed_lines)

    # Ro‘yxatlar
    text = text.replace('\n* ', '\n• ')
    text = text.replace('\n- ', '\n• ')

    # Qalin va kursiv
    while '**' in text:
        text = text.replace('**', '<b>', 1)
        text = text.replace('**', '</b>', 1)

    while '__' in text:
        text = text.replace('__', '<i>', 1)
        text = text.replace('__', '</i>', 1)

    # Kod
    while '`' in text:
        text = text.replace('`', '<code>', 1)
        text = text.replace('`', '</code>', 1)

    return text


@dp.message(ChatStates.gemini)
@rate_limit(limit=10, period=60)
async def chat_with_gemini(message: Message, state: FSMContext):
    """Foydalanuvchi yuborgan xabarni Google Gemini API ga jo‘natadi va javobini qaytaradi."""
    user_id = str(message.from_user.id)
    user_message = message.text

    try:
        await bot.send_chat_action(chat_id=user_id, action="typing")

        # Strukturalangan prompt
        structured_prompt = (
            "Respond in plain text format without using markdown or special formatting. "
            "Use simple bullet points (•) for lists and regular text for everything else. "
            "If the question is in Uzbek, answer in Uzbek.\n\n"
            f"Question: {user_message}"
        )

        # Gemini chat ni boshlash
        chat = model.start_chat()
        response = chat.send_message(structured_prompt)

        await state.set_state(GeminiAnswering.answering)

        # Javobni tozalash va formatlash
        bot_response = response.text.strip()

        # Xabarni yuborish
        if len(bot_response) > 4096:
            for x in range(0, len(bot_response), 4096):
                await message.reply(
                    bot_response[x:x + 4096],
                    parse_mode=None  # HTML parse mode ni o‘chirish
                )
        else:
            await message.reply(
                bot_response,
                parse_mode=None  # HTML parse mode ni o‘chirish
            )

        # Bot javobini saqlash
        gemini_data_manager.add_message(user_id, "assistant", bot_response)

        await state.set_state(ChatStates.gemini)

    except Exception as e:
        logger.error(f"Error in chat handler: {e}")
        await message.reply(
            "Kechirasiz, xatolik yuz berdi. "
            "Iltimos qaytadan urinib ko‘ring."
        )
