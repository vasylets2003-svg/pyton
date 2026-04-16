import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# ВАШІ НАЛАШТУВАННЯ
API_TOKEN = '8227869466:AAEzjHRVuC8zAfaW9MEkUYaNMekK8ivLgBg'
ADMIN_ID = 940533533

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Привітання
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Вітаю! Надішліть сюди домен, який потрібно розблокувати, і я передам заявку адміністратору.")

# Пересилка повідомлень від користувача до вас
@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    await bot.forward_message(chat_id=ADMIN_ID, from_chat_id=message.chat.id, message_id=message.message_id)
    await message.answer("✅ Заявку прийнято. Адміністратор скоро з вами зв'яжеться.")

# Відповідь вам (якщо ви робите Reply на повідомлення)
@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    user_id = message.reply_to_message.forward_from.id
    await bot.send_message(user_id, f"Відповідь від підтримки:\n\n{message.text}")
    await message.answer("Відправлено користувачу!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())