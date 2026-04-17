import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Токен з налаштувань Render
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# Словник для пам'яті (ID повідомлення адміна : ID користувача)
user_registry = {}

@dp.message(F.chat.id != 940533533)
async def send_to_admin(message: types.Message):
    # Отримуємо ім'я та логін
    user_info = f"{message.from_user.full_name}"
    if message.from_user.username:
        user_info += f" (@{message.from_user.username})"
    
    # Відправляємо адміну
    msg = await bot.send_message(
        940533533, 
        f"📩 Заявка: {message.text}\n👤 Хто: {user_info}\n🆔 ID: {message.chat.id}"
    )
    
    # Зберігаємо ID у пам'яті
    user_registry[msg.message_id] = message.chat.id
    await message.answer("✅ Прийнято.")

@dp.message(F.chat.id == 940533533, F.reply_to_message)
async def admin_reply(message: types.Message):
    # Беремо ID клієнта зі словника за ID повідомлення, на яке ми відповіли
    target_id = user_registry.get(message.reply_to_message.message_id)
    
    if target_id:
        await bot.send_message(target_id, f"Відповідь від Віки:\n{message.text}")
        await message.answer("✅ Відправлено!")
    else:
        await message.answer("❌ Не можу знайти дані про цього клієнта (можливо, бот був перезапущений).")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
