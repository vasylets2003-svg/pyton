import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

API_TOKEN = 'ВАШ_ТОКЕН_З_BOTFATHER'
ADMIN_ID = 940533533 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Цей словник зберігає зв'язок: {ID повідомлення адміна: ID користувача}
# Ми будемо записувати сюди ID користувача автоматично
user_registry = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.id == ADMIN_ID:
        await message.answer("Бот працює! Очікую на заявки.")
    else:
        await message.answer("Напишіть домен, який потрібно розблокувати.")

# 1. ОТРИМАННЯ ПОВІДОМЛЕННЯ ВІД КЛІЄНТА
@dp.message(F.chat.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
    # Замість пересилання (forward) ми просто копіюємо текст
    # Це працює, навіть якщо у клієнта заборонено пересилання
    admin_msg = await bot.send_message(
        ADMIN_ID, 
        f"📩 Заявка від користувача:\n\n{message.text}\n\n(ID: {message.chat.id})"
    )
    
    # Запам'ятовуємо, що це повідомлення належить цьому користувачу
    user_registry[admin_msg.message_id] = message.chat.id
    
    await message.answer("✅ Заявку прийнято, чекайте на відповідь.")

# 2. ВІДПОВІДЬ АДМІНА
@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user(message: types.Message):
    # Беремо ID повідомлення, на яке ми відповіли
    replied_id = message.reply_to_message.message_id
    
    # Шукаємо в нашому словнику ID користувача
    user_id = user_registry.get(replied_id)
    
    if user_id:
        try:
            await bot.send_message(user_id, f"Відповідь від Віки:\n\n{message.text}")
            await message.answer("✅ Відправлено!")
        except Exception as e:
            await message.answer(f"❌ Помилка: {e}")
    else:
        await message.answer("❌ Не можу знайти ID клієнта. Спробуйте відповісти на інше повідомлення.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
