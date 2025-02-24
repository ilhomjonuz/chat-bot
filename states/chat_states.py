from aiogram.fsm.state import StatesGroup, State


class ChatStates(StatesGroup):
    openai = State()
    gemini = State()


class OpenAIAnswering(StatesGroup):
    answering = State()


class GeminiAnswering(StatesGroup):
    answering = State()
