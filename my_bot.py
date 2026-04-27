import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- НАЛАШТУВАННЯ ---
API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 940533533  # Ваш ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
# Словник для зв'язку: {ID повідомлення адміна : ID клієнта}
user_registry = {}

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Бот працює!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    # Використовуємо порт, який надає Render
    port = int(os.getenv('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- ЛОГІКА БОТА ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.id == ADMIN_ID:
        await message.answer("Вітаю, Віко! Бот на зв'язку.")
    else:
        await message.answer("Привіт! Напишіть, що вас цікавить.")

@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    # 1. Відправляємо текстову інформацію
    name = message.from_user.full_name
    username = f" (@{message.from_user.username})" if message.from_user.username else ""
    
    admin_msg = await bot.send_message(
        ADMIN_ID, 
        f"📩 Заявка від: {name}{username}\n🆔 ID: {message.chat.id}"
    )
    
    # 2. Копіюємо контент (фото, відео, текст, стікер)
    await bot.copy_message(
        chat_id=ADMIN_ID, 
        from_chat_id=message.chat.id, 
        message_id=message.message_id
    )
    
    # Зберігаємо зв'язок
    user_registry[admin_msg.message_id] = message.chat.id
    await message.answer("✅ Заявку прийнято. Чекайте на відповідь.")

@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    # Шукаємо ID клієнта за ID повідомлення, на яке відповіли
    replied_id = message.reply_to_message.message_id
    user_id = user_registry.get(replied_id)
    
    if user_id:
        try:
            # Якщо адмін пише текст
            if message.text:
                await bot.send_message(user_id, f"Відповідь від Віки:\n\n{message.text}")
            # Якщо адмін відправляє фото/відео
            else:
                await bot.copy_message(user_id, message.chat.id, message.message_id)
                
            await message.answer("✅ Відправлено!")
        except Exception as e:
            await message.answer(f"❌ Помилка: {e}")
    else:
        await message.answer("❌ Не можу знайти ID. Можливо, бот перезавантажився.")

# --- ЗАПУСК ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
