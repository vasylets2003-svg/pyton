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

# --- ВЕБ-СЕРВЕР (ДЛЯ RENDER) ---
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

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.id == ADMIN_ID:
        await message.answer("Вітаю, Віко! Бот на зв'язку.")
    else:
        await message.answer("Привіт! Напишіть своє запитання.")

# 1. Пересилка до адміна з усіма даними
@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    # Збираємо дані користувача
    name = message.from_user.full_name
    username = f" (@{message.from_user.username})" if message.from_user.username else ""
    
    # Створюємо повідомлення з усією інфою
    info_text = f"📩 Заявка від: {name}{username}\n🆔 ID: {message.chat.id}"
    
    # Відправляємо текст
    await bot.send_message(ADMIN_ID, info_text)
    
    # Копіюємо контент (фото, відео, текст)
    await bot.copy_message(
        chat_id=ADMIN_ID, 
        from_chat_id=message.chat.id, 
        message_id=message.message_id
    )
    await message.answer("✅ Заявку прийнято. Чекайте на відповідь.")

# 2. Відповідь адміна
@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    original_msg = message.reply_to_message
    
    # Шукаємо ID в тексті або в описі (caption) фото
    content = original_msg.text or original_msg.caption or ""
    
    if "🆔 ID: " in content:
        try:
            # Витягуємо ID
            target_id = content.split("🆔 ID: ")[1].split("\n")[0].strip()
            
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
        await message.answer("❌ Не можу знайти ID. Відповідайте на текстове повідомлення з ID.")

# --- ЗАПУСК ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
