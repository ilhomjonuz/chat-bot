from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env fayl ichidan quyidagilarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot toekn
ADMINS = env.list("ADMINS")  # adminlar ro'yxati
IP = env.str("ip")  # Xosting ip manzili

OPENAI_API_KEY = env.str("OPENAI_API_KEY")
OPENAI_MODEL = env.str("OPENAI_MODEL")
GEMINI_API_KEY = env.str("GEMINI_API_KEY")
GEMINI_MODEL = env.str("GEMINI_MODEL")
