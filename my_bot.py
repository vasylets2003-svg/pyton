import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# ВАШІ НАЛАШТУВАННЯ
API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 940533533

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
user_registry = {}

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (щоб не вимикав бота) ---
async def handle(request):
    return web.Response(text="Бот активний")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

# --- ЛОГІКА БОТА ---
async def heartbeat():
    while True:
        await asyncio.sleep(86400) # Чекати 24 години
        await bot.send_message(ADMIN_ID, "🤖 Бот на зв'язку! Все працює стабільно.")
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.id == ADMIN_ID:
        await message.answer("Вітаю, Віко! Бот на зв'язку.")
    else:
        await message.answer("Привіт! Напишіть домен, який потрібно розблокувати.")

@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    # Копіюємо текст клієнта (працює завжди)
    admin_msg = await bot.send_message(
        ADMIN_ID, 
        f"📩 Заявка:\n{message.text}\n\nID користувача: {message.chat.id}"
    )
    # Зберігаємо ID
    user_registry[admin_msg.message_id] = message.chat.id
    await message.answer("✅ Заявку прийнято.")

@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    # Беремо ID, на яке відповіли
    replied_id = message.reply_to_message.message_id
    user_id = user_registry.get(replied_id)
    
    if user_id:
        try:
            await bot.send_message(user_id, f"Відповідь від Віки:\n\n{message.text}")
            await message.answer("✅ Відправлено!")
        except Exception as e:
            await message.answer(f"❌ Помилка: {e}")
    else:
        await message.answer("❌ Не можу знайти ID в цьому повідомленні.")

async def main():
    async def main():
    await start_web_server()
    asyncio.create_task(heartbeat()) # Запускаємо фонову задачу "серцебиття"
    await dp.start_polling(bot)
    # Запускаємо веб-сервер та бота
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
