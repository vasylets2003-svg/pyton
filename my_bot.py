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

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Бот працює!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- ЛОГІКА БОТА ---

@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    # Відправляємо текст з ID
    await bot.send_message(
        ADMIN_ID, 
        f"📩 Заявка від: {message.from_user.full_name}\n🆔 ID: {message.chat.id}"
    )
    # Копіюємо контент (фото, відео, текст, гіфки)
    await bot.copy_message(
        chat_id=ADMIN_ID, 
        from_chat_id=message.chat.id, 
        message_id=message.message_id
    )
    await message.answer("✅ Заявку прийнято.")

@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    # Беремо текст повідомлення, на яке відповідаємо
    reply_text = message.reply_to_message.text or ""
    
    # Витягуємо ID з тексту (шукаємо "🆔 ID: ")
    if "🆔 ID: " in reply_text:
        try:
            target_id = reply_text.split("🆔 ID: ")[1].split("\n")[0].strip()
            
            # Якщо адмін пише текст
            if message.text:
                await bot.send_message(target_id, f"Відповідь від Віки:\n\n{message.text}")
            # Якщо адмін відправляє фото/відео/гіфку
            else:
                await bot.copy_message(target_id, message.chat.id, message.message_id)
                
            await message.answer("✅ Відправлено!")
        except Exception as e:
            await message.answer(f"❌ Помилка: {e}")
    else:
        await message.answer("❌ Відповідайте на повідомлення, де є '🆔 ID: '")

async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
