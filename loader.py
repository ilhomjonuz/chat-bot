from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from data import config
from utils.json_manager import JSONDataManager

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

openai_data_manager = JSONDataManager()
gemini_data_manager = JSONDataManager(file_path='data/chat_story/gemini_data.json')