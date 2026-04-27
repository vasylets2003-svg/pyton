import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- НАЛАШТУВАННЯ ---
API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 940533533

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- ВЕБ-СЕРВЕР ---
async def start_web_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 10000)))
    await site.start()

# --- ЛОГІКА БОТА ---

@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    # Запобіжник від None: якщо ім'я порожнє, пишемо "Користувач"
    name = message.from_user.full_name if message.from_user else "Користувач"
    
    # Відправляємо текст з ID
    # Важливо: формат "ID: [цифри]" має бути точним
    admin_text = f"📩 Заявка від: {name}\n🆔 ID: {message.chat.id}"
    await bot.send_message(ADMIN_ID, admin_text)
    
    # Копіюємо контент (фото, відео, текст)
    await bot.copy_message(ADMIN_ID, message.chat.id, message.message_id)
    
    await message.answer("✅ Заявку прийнято.")

@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    # Беремо текст повідомлення, на яке відповіли (або підпис до фото/відео)
    original = message.reply_to_message
    content = original.text or original.caption or ""
    
    # Шукаємо ID
    if "🆔 ID: " in content:
        try:
            # Розрізаємо рядок, щоб дістати число після "🆔 ID: "
            target_id = content.split("🆔 ID: ")[1].split("\n")[0].strip()
            
            # Якщо адмін пише текст - відправляємо текст
            if message.text:
                await bot.send_message(target_id, f"Відповідь від адміна:\n\n{message.text}")
            # Якщо адмін відправляє фото/відео - копіюємо його
            else:
                await bot.copy_message(target_id, message.chat.id, message.message_id)
                
            await message.answer("✅ Відправлено!")
        except Exception as e:
            await message.answer(f"❌ Помилка при відправці: {e}")
    else:
        await message.answer("❌ Не знайдено ID в цьому повідомленні. Відповідайте на 'Заявку', де є ID.")

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
