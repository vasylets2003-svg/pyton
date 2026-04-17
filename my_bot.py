import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Отримуємо токен з Render (Environment Variables)
API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 940533533

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_registry = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.id == ADMIN_ID:
        await message.answer("Вітаю, Віко! Бот працює.")
    else:
        await message.answer("Напишіть домен, який потрібно розблокувати.")

@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    admin_msg = await bot.send_message(
        ADMIN_ID, 
        f"📩 Заявка: {message.text}\n\nID користувача: {message.chat.id}"
    )
    user_registry[admin_msg.message_id] = message.chat.id
    await message.answer("✅ Прийнято.")

@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    replied_id = message.reply_to_message.message_id
    user_id = user_registry.get(replied_id)
    
    if user_id:
        try:
            await bot.send_message(user_id, f"Відповідь від Віки:\n\n{message.text}")
            await message.answer("✅ Відправлено!")
        except Exception as e:
            await message.answer(f"❌ Помилка: {e}")
    else:
        await message.answer("❌ Не можу знайти ID клієнта.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
