import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineQuery, InlineQueryResultVoice
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

# 🔒 Faqat bitta foydalanuvchi uchun (o'zingizning Telegram ID ni yozing)
OWNER_ID = 595959200  # <-- bu yerga o'zingizning Telegram ID ni yozasiz

# 🔑 Bot tokenini atrof-muhitdan olish (Render uchun)
TOKEN = os.getenv("BOT_TOKEN")

# diagnostika (faqat qisqa vaqtga, tokenni chop etmang)
if TOKEN is None:
    raise SystemExit("ENV ERROR: BOT_TOKEN is not set in environment variables.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📁 Ovozlar papkasi
VOICE_DIR = "voices"
os.makedirs(VOICE_DIR, exist_ok=True)

# 🎙 Ovoz qo‘shish
@dp.message(Command("addvoice"))
async def add_voice(message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.answer("❌ Bu botdan foydalanish taqiqlangan.")

    if not message.reply_to_message or not message.reply_to_message.voice:
        return await message.answer("❗ Iltimos, ovozli xabarga javoban /addvoice <nom> deb yozing.")
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.answer("❗ Ovoz nomini ham yozing: /addvoice salom")

    name = args[1].strip().lower()
    file_id = message.reply_to_message.voice.file_id
    file = await bot.get_file(file_id)
    path = os.path.join(VOICE_DIR, f"{name}.ogg")
    await bot.download_file(file.file_path, path)
    await message.answer(f"✅ Ovoz saqlandi: {name}")

# 🔍 Inline orqali ovoz qidirish
@dp.inline_query()
async def inline_query(query: InlineQuery):
    if query.from_user.id != OWNER_ID:
        return  # Boshqalar foydalana olmaydi

    results = []
    for file in os.listdir(VOICE_DIR):
        if query.query.lower() in file.lower() and file.endswith(".ogg"):
            voice_url = f"https://your-render-url.onrender.com/{VOICE_DIR}/{file}"
            results.append(
                InlineQueryResultVoice(
                    id=file,
                    title=file.replace(".ogg", ""),
                    voice_url=voice_url
                )
            )

    await query.answer(results, cache_time=0)

# 🏠 /start komandasi
@dp.message(Command("start"))
async def start(message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.answer("❌ Sizga bu botdan foydalanish ruxsati yo‘q.")
    await message.answer("👋 Salom! Ovozli xabarni /addvoice <nom> orqali saqlang.")

# 🚀 Botni ishga tushirish
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
