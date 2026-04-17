import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

@dp.message(F.chat.id != 940533533)
async def send_to_admin(message: types.Message):
    # Отримуємо дані
    name = message.from_user.full_name
    username = f" (@{message.from_user.username})" if message.from_user.username else ""
    
    # ВАЖЛИВО: Ми ховаємо ID в кінці повідомлення, 
    # щоб при відповіді (Reply) ми могли його легко прочитати
    text = f"📩 Заявка: {message.text}\n👤 Хто: {name}{username}\n🆔 ID:{message.chat.id}"
    
    await bot.send_message(940533533, text)
    await message.answer("✅ Заявку прийнято.")

@dp.message(F.chat.id == 940533533, F.reply_to_message)
async def admin_reply(message: types.Message):
    # Беремо текст повідомлення, на яке ми відповіли
    original_text = message.reply_to_message.text
    
    try:
        # Шукаємо "🆔 ID:" і витягуємо все, що після нього
        if "🆔 ID: " in original_text:
            target_id = original_text.split("🆔 ID: ")[1].strip()
            
            # Відправляємо відповідь
            await bot.send_message(target_id, f"Відповідь від Віки:\n\n{message.text}")
            await message.answer("✅ Відправлено!")
        else:
            await message.answer("❌ Не можу знайти ID в цьому повідомленні.")
    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
