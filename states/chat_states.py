from aiogram.fsm.state import StatesGroup, State


class ChatStates(StatesGroup):
    openai = State()
    gemini = State()
    deepseek = State()


class OpenAIAnswering(StatesGroup):
    answering = State()


class GeminiAnswering(StatesGroup):
    answering = State()


class DeepSeekAnswering(StatesGroup):
    answering = State()
