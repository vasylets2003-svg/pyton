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

# --- ВЕБ-СЕРВЕР (ДЛЯ RENDER) ---
async def handle(request):
    return web.Response(text="Бот працює!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    # Використовуємо порт з Render або 10000 за замовчуванням
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

# 1. Пересилка від користувача до адміна
@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    # Відправляємо текстову "шапку" з ID
    await bot.send_message(
        ADMIN_ID, 
        f"📩 Заявка від: {message.from_user.full_name} (@{message.from_user.username})\n🆔 ID: {message.chat.id}"
    )
    
    # Копіюємо контент (фото, відео, текст, гіфки)
    await bot.copy_message(
        chat_id=ADMIN_ID, 
        from_chat_id=message.chat.id, 
        message_id=message.message_id
    )
    await message.answer("✅ Заявку прийнято. Чекайте на відповідь.")

# 2. Відповідь від адміна до користувача
@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    # Беремо повідомлення, на яке відповів адмін
    original_msg = message.reply_to_message
    
    # Шукаємо текст або опис (якщо це було фото/відео)
    content = original_msg.text or original_msg.caption or ""
    
    # Шукаємо ID в тексті
    if "🆔 ID: " in content:
        try:
            target_id = content.split("🆔 ID: ")[1].split("\n")[0].strip()
            
            # Якщо адмін пише текст
            if message.text:
                await bot.send_message(target_id, f"Відповідь від Віки:\n\n{message.text}")
            # Якщо адмін відправляє фото/відео/документ
            else:
                await bot.copy_message(target_id, message.chat.id, message.message_id)
                
            await message.answer("✅ Відправлено!")
        except Exception as e:
            await message.answer(f"❌ Помилка: {e}")
    else:
        await message.answer("❌ Не можу знайти ID. Відповідайте на повідомлення з текстом '🆔 ID: '")

# --- ЗАПУСК ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server() # Запускаємо сервер для Render
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
