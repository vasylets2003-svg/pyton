import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 940533533

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словник: {ID повідомлення адміна : ID клієнта}
# Це працює в пам'яті бота, поки він не перезавантажиться
user_registry = {}

@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    # Отримуємо юзернейм або ID
    username = f"@{message.from_user.username}" if message.from_user.username else "Без логіна"
    
    # Відправляємо адміну заявку
    admin_msg = await bot.send_message(
        ADMIN_ID, 
        f"📩 Заявка: {message.text}\n👤 Логін: {username}\n🆔 ID: {message.chat.id}"
    )
    
    # ЗАПАМ'ЯТОВУЄМО ПРЯМО В ПАМ'ЯТІ
    user_registry[admin_msg.message_id] = message.chat.id
    
    await message.answer("✅ Заявку прийнято.")

@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    # Беремо ID повідомлення, на яке ми відповіли
    replied_id = message.reply_to_message.message_id
    
    # Шукаємо в словнику
    user_id = user_registry.get(replied_id)
    
    if user_id:
        await bot.send_message(user_id, f"Відповідь від Віки:\n\n{message.text}")
        await message.answer("✅ Відправлено!")
    else:
        await message.answer("❌ Не можу знайти цей ID у пам'яті (можливо, був перезапуск).")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
