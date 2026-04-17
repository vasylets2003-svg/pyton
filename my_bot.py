import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Токен береться з налаштувань Render (Environment Variables)
API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 940533533

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# 1. ОБРОБКА ЗАЯВОК
@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    # Отримуємо логін клієнта
    user_display = f"@{message.from_user.username}" if message.from_user.username else "Без логіна"
    
    # Надсилаємо адміну повідомлення з усіма даними
    await bot.send_message(
        ADMIN_ID, 
        f"📩 Заявка: {message.text}\n\n👤 Логін: {user_display}\nID користувача: {message.chat.id}"
    )
    await message.answer("✅ Заявку прийнято, чекайте на відповідь.")

# 2. ВІДПОВІДЬ АДМІНА (НАДІЙНА)
@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    original_text = message.reply_to_message.text
    
    # Шукаємо ID прямо в тексті повідомлення, на яке відповідаємо
    if "ID користувача: " in original_text:
        try:
            user_id = int(original_text.split("ID користувача: ")[1].strip())
            await bot.send_message(user_id, f"Відповідь від Віки:\n\n{message.text}")
            await message.answer("✅ Відправлено!")
        except Exception as e:
            await message.answer(f"❌ Помилка: {e}")
    else:
        await message.answer("❌ Не можу знайти ID клієнта в цьому повідомленні.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
