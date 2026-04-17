import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()
user_registry = {}

# --- ВЕБ-СЕРВЕР ---
async def handle(request):
    return web.Response(text="Бот працює")

async def run_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()

# --- ЛОГІКА БОТА ---
@dp.message(F.chat.id != 940533533)
async def send_to_admin(message: types.Message):
    user_info = f"{message.from_user.full_name} (@{message.from_user.username})" if message.from_user.username else f"{message.from_user.full_name}"
    msg = await bot.send_message(940533533, f"📩 Заявка: {message.text}\n👤 Хто: {user_info}\n🆔 ID: {message.chat.id}")
    user_registry[msg.message_id] = message.chat.id
    await message.answer("✅ Прийнято.")

@dp.message(F.chat.id == 940533533, F.reply_to_message)
async def admin_reply(message: types.Message):
    target_id = user_registry.get(message.reply_to_message.message_id)
    if target_id:
        await bot.send_message(target_id, f"Відповідь від Віки:\n{message.text}")
        await message.answer("✅ Відправлено!")

async def main():
    await run_web_server()  # Запускаємо веб-сервер для Render
    await dp.start_polling(bot) # Запускаємо бота

if __name__ == "__main__":
    asyncio.run(main())
