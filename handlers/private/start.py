from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from keyboards.reply import menu_keyboard
from loader import dp


@dp.message(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer(
        f"Salom, {message.from_user.full_name}! Men chatbot-man, suhbatlashish uchun bo‘limni tanlang",
        reply_markup=await menu_keyboard()
    )
    await state.clear()
