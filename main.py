from aiogram import Bot, Dispatcher, executor
from bot.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

if __name__ == "__main__":
    from bot.handlers import start, comment_check  # handlerlarni chaqirish
    executor.start_polling(dp, skip_updates=True)
