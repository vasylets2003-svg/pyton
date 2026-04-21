import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# --- НАЛАШТУВАННЯ ---
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

# --- ФУНКЦІЇ БОТА ---

@dp.message(F.chat.id != 940533533)
async def send_to_admin(message: types.Message):
    name = message.from_user.full_name
    username = f" (@{message.from_user.username})" if message.from_user.username else ""
    
    # Формуємо текст
    text = f"📩 Заявка: {message.text}\n👤 Хто: {name}{username}\n🆔 ID: {message.chat.id}"
    
    await bot.send_message(940533533, text)
    await message.answer("✅ Заявку прийнято.")

@dp.message(F.chat.id == 940533533, F.reply_to_message)
async def admin_reply(message: types.Message):
    original_text = message.reply_to_message.text
    
    try:
        # Шукаємо "ID: " (з пробілом!)
        if "ID: " in original_text:
            target_id = original_text.split("ID: ")[1].split("\n")[0].strip()
            
            await bot.send_message(target_id, f"Відповідь від Віки:\n\n{message.text}")
            await message.answer("✅ Відправлено!")
        else:
            await message.answer("❌ Не можу знайти ID. Переконайтеся, що в повідомленні є 'ID: '")
    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")

# --- ВЕБ-ЗАГЛУШКА (ДЛЯ RENDER) ---

async def health_check(request):
    return web.Response(text="Бот працює!")

async def main():
    # 1. Запускаємо веб-сервер
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    # Беремо порт з налаштувань Render, або 8080 за замовчуванням
    port = int(os.getenv('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    # 2. Запускаємо бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
