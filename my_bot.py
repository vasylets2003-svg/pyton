import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Токен береться з налаштувань Render (Environment Variables)
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# Словник для зберігання зв'язку: {ID повідомлення адміна : ID користувача}
user_registry = {}

@dp.message(F.chat.id != 940533533)
async def send_to_admin(message: types.Message):
    # --- ОТРИМУЄМО ДАНІ ПРО КОРИСТУВАЧА ---
    # Повне ім'я (наприклад: Вікторія)
    full_name = message.from_user.full_name
    # Логін (наприклад: @vika_user), якщо є
    username = f" (@{message.from_user.username})" if message.from_user.username else ""
    
    # Формуємо детальне повідомлення
    user_info = f"{full_name}{username}"
    
    # Надсилаємо адміну
    msg = await bot.send_message(
        940533533, 
        f"📩 Заявка: {message.text}\n"
        f"👤 Користувач: {user_info}\n"
        f"🆔 ID: {message.chat.id}"
    )
    
    # Запам'ятовуємо зв'язок
    user_registry[msg.message_id] = message.chat.id
    await message.answer("✅ Заявку прийнято. Чекайте на відповідь.")

@dp.message(F.chat.id == 940533533, F.reply_to_message)
async def admin_reply(message: types.Message):
    # Отримуємо ID користувача з нашої "пам'яті"
    target_id = user_registry.get(message.reply_to_message.message_id)
    
    if target_id:
        await bot.send_message(target_id, f"Відповідь від Віки:\n\n{message.text}")
        await message.answer("✅ Відправлено!")
    else:
        await message.answer("❌ Помилка: не можу знайти ID клієнта в пам'яті (можливо, бот перезавантажився).")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
