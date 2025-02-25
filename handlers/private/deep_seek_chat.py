import logging
from typing import List, Dict

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent
from openai import AsyncOpenAI

from data.config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL
from loader import dp, bot, deepseek_data_manager
from states import ChatStates, DeepSeekAnswering

logger = logging.getLogger(__name__)


# DeepSeek AI uchun handler
@dp.message(F.text == '🚀 DeepSeek AI')
async def deepseek_chat_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    deepseek_data_manager.clear_history(user_id)

    text = "DeepSeek AI model orqali javob beriladi!\nSavolingizni yuboring"
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ChatStates.deepseek)

# DeepSeek AI uchun async client
client_deepseek = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


async def stream_response_deepseek(message: types.Message, messages: List[Dict]) -> str:
    """DeepSeek AI modelidan streaming javobni olish"""
    try:
        stream = await client_deepseek.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
            stream=True  # Streaming yoqilgan
        )

        full_response = ""
        temp_message = await message.reply("Thinking...")

        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                if len(full_response) % 100 == 0:  # Har 100 ta belgi yangilash
                    await temp_message.edit_text(full_response[:4096])

        await temp_message.edit_text(full_response[:4096])
        return full_response

    except Exception as e:
        logger.error(f"DeepSeek AI streaming error: {e}")
        raise


@dp.message(ChatStates.deepseek)
async def chat_handle_message_deepseek(message: types.Message, state: FSMContext):
    """DeepSeek AI uchun foydalanuvchi so‘rovini qayta ishlash"""
    user_id = str(message.from_user.id)
    user_message = message.text

    try:
        await bot.send_chat_action(chat_id=user_id, action="typing")

        # Foydalanuvchi xabarini tarixga qo‘shish
        deepseek_data_manager.add_message(user_id, "user", user_message)
        messages = deepseek_data_manager.manage_conversation_history(user_id, max_messages=5)

        # Javobni stream orqali olish
        bot_response = await stream_response_deepseek(message, messages)

        await state.set_state(DeepSeekAnswering.answering)

        # Model javobini tarixga qo‘shish
        deepseek_data_manager.add_message(user_id, "assistant", bot_response)

        await state.set_state(ChatStates.deepseek)

    except Exception as e:
        error_msg = "Hisobingizda yetarli mablag‘ yo‘q. Iltimos, DeepSeek AI balansingizni tekshiring." if "payment" in str(
            e).lower() else "Xatolik yuz berdi. Qaytadan urinib ko‘ring."
        logger.error(f"DeepSeek chat error for user {user_id}: {e}")
        await message.reply(error_msg)


@dp.error(ChatStates.deepseek)
async def deepseek_error_handler(event: ErrorEvent) -> bool:
    try:
        error_msg = "Rate limit exceeded. Please wait." if "rate" in str(
            event.exception).lower() else "An error occurred. Please try again."

        if event.update.message:
            await event.update.message.answer(error_msg)

        logger.error(
            "DeepSeek AI Error: %s\nUpdate: %s",
            event.exception,
            event.update
        )
    except Exception as e:
        logger.error(f"Error in DeepSeek error handler: {e}")
    return True
