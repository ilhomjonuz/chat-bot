import logging
from typing import List, Dict

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent
from openai import AsyncOpenAI

from data.config import OPENAI_API_KEY, OPENAI_MODEL
from loader import dp, bot, openai_data_manager
from states import ChatStates, OpenAIAnswering

logger = logging.getLogger(__name__)


@dp.message(F.text == '🧠 OpenAI')
async def openai_chat_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    openai_data_manager.clear_history(user_id)

    text = "OpenAI model orqali javob beriladi!\nSavolingizni yuboring"
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ChatStates.openai)


@dp.message(OpenAIAnswering.answering)
async def typing_openai_bot(message: types.Message):
    await message.reply("⚠️ Iltimos, xabarlar orasida ozgina kutib turing!")


# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def stream_response(message: types.Message, messages: List[Dict]) -> str:
    """Stream the AI response and update the message"""
    try:
        stream = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
            stream=True  # Enable streaming
        )

        full_response = ""
        temp_message = await message.reply("Thinking...")

        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                if len(full_response) % 100 == 0:  # Update every 100 chars
                    await temp_message.edit_text(full_response[:4096])

        await temp_message.edit_text(full_response[:4096])
        return full_response

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        raise


@dp.message(ChatStates.openai)
async def chat_handle_message(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_message = message.text

    try:
        await bot.send_chat_action(chat_id=user_id, action="typing")

        # Add user message to history
        openai_data_manager.add_message(user_id, "user", user_message)
        messages = openai_data_manager.manage_conversation_history(user_id, max_messages=5)

        # Stream the response
        bot_response = await stream_response(message, messages)

        await state.set_state(OpenAIAnswering.answering)

        # Add bot response to history
        openai_data_manager.add_message(user_id, "assistant", bot_response)

        await state.set_state(ChatStates.openai)

    except Exception as e:
        error_msg = "Rate limit exceeded. Please wait." if "rate" in str(
            e).lower() else "An error occurred. Please try again."
        logger.error(f"Chat error for user {user_id}: {e}")
        await message.reply(error_msg)


@dp.error(ChatStates.openai)
async def error_handler(event: ErrorEvent) -> bool:
    try:
        error_msg = "Rate limit exceeded. Please wait." if "rate" in str(
            event.exception).lower() else "An error occurred. Please try again."

        if event.update.message:
            await event.update.message.answer(error_msg)

        logger.error(
            "Error occurred: %s\nUpdate: %s",
            event.exception,
            event.update
        )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")
    return True
