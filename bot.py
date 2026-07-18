import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
import aiohttp
import json
import os
import threading
import time

API_TOKEN = "8695836578:AAH7LO-Bu6tMXTjvu4yE-Co38Uqkw09TU5Q"
ADMIN_ID = 7781474535
GEMINI_API = "AQ.Ab8RN6I5tvV2ZCvCU03Hi81xWWmohhnzC76nVALV-hL7Kk3izg"
USERS_FILE = "users.json"
PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    waiting_bug = State()
    waiting_player = State()
    waiting_join = State()
    waiting_question = State()
    waiting_ai = State()
    waiting_broadcast = State()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return set(json.load(f))
    return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(list(users), f)

users = load_users()

def main_menu():
    kb = [
        [KeyboardButton(text="🐛 Баги и дюпы")],
        [KeyboardButton(text="👤 Жалоба на игрока / КП")],
        [KeyboardButton(text="📝 Подача в часть проекта")],
        [KeyboardButton(text="❓ Вопрос администрации")],
        [KeyboardButton(text="⛄ Правила сервера")],
        [KeyboardButton(text="🤖 AI-ассистент")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cancel_keyboard():
    kb = [[KeyboardButton(text="🔙 Отмена")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

async def handle_health(request):
    return web.Response(text="OK")

# ===== ОТМЕНА =====
@dp.message(F.text == "🔙 Отмена")
async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer("❌ Действие отменено.", reply_markup=main_menu())

# ===== РАССЫЛКА =====
@dp.message(Command("broadcast"))
async def broadcast_cmd(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(Form.waiting_broadcast)
    await message.answer("📢 Введите сообщение для рассылки:")

@dp.message(Form.waiting_broadcast)
async def broadcast_send(message: types.Message, state: FSMContext):
    text = message.text
    success, fail = 0, 0
    for user_id in users:
        try:
            await bot.send_message(user_id, f"📢 *Рассылка ColdWorld:*\n\n{text}", parse_mode="Markdown")
            success += 1
        except:
            fail += 1
        await asyncio.sleep(0.1)
    await message.answer(f"✅ Успешно: {success}, Не доставлено: {fail}")
    await state.clear()

# ===== ПРАВИЛА =====
@dp.message(F.text == "⛄ Правила сервера")
async def rules(message: types.Message):
    kb = [[InlineKeyboardButton(text="📜 Открыть правила", url="https://t.me/coldworld_pravila")]]
    await message.answer("Нажмите кнопку ниже чтобы открыть правила:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

# ===== AI =====
@dp.message(F.text == "🤖 AI-ассистент")
async def ai_start(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_ai)
    await message.answer("🤖 *AI-ассистент*\n\nЗадайте вопрос:", parse_mode="Markdown", reply_markup=cancel_keyboard())

@dp.message(Form.waiting_ai)
async def ai_answer(message: types.Message, state: FSMContext):
    temp_msg = await message.answer("🤔 *Думаю...*", parse_mode="Markdown")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API}",
                json={"contents": [{"parts": [{"text": message.text}]}]}
            ) as resp:
                data = await resp.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        reply = "❌ Ошибка AI."
    await temp_msg.delete()
    await message.answer(f"🤖 *Ответ:*\n\n{reply}", parse_mode="Markdown", reply_markup=main_menu())
    await state.clear()

# ===== ОТВЕТ =====
@dp.message(Command("reply"))
async def reply_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("/reply ID текст")
        return
    try:
        await bot.send_message(int(args[1]), f"📩 *Ответ администрации:*\n\n{args[2]}", parse_mode="Markdown")
        await message.answer("✅ Отправлено!")
    except:
        await message.answer("❌ Ошибка!")

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    users.add(message.from_user.id)
    save_users(users)
    await message.answer(
        "❄️ *Добро пожаловать в ColdWorld!*\n\n"
        "✨ *Я могу помочь тебе:*\n"
        "• 🐛 Сообщить о багах и дюпах\n"
        "• 👤 Подать жалобу на игрока или КП\n"
        "• 📝 Подать заявку в часть проекта\n"
        "• ❓ Задать вопрос администрации\n"
        "• ⛄ Узнать правила сервера\n"
        "• 🤖 Спросить у AI-ассистента",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ===== БАГИ =====
@dp.message(F.text == "🐛 Баги и дюпы")
async def bug_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_bug)
    await message.answer("🐛 *Баг-репорт*\n\nОпишите проблему:\n• Никнейм в игре\n• Описание бага\n\nПриложите скриншот.", parse_mode="Markdown", reply_markup=cancel_keyboard())

@dp.message(Form.waiting_bug)
async def bug_done(message: types.Message, state: FSMContext):
    user = message.from_user
    await bot.send_message(ADMIN_ID, f"🐛 *Баг от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
    await message.answer("✅ Отправлено!", reply_markup=main_menu())
    await state.clear()

# ===== ЖАЛОБЫ =====
@dp.message(F.text == "👤 Жалоба на игрока / КП")
async def player_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_player)
    await message.answer("👤 *Жалоба*\n\nУкажите:\n• Никнейм нарушителя\n• Что произошло\n• Доказательства\n\n⚠️ Ложные жалобы наказуемы.", parse_mode="Markdown", reply_markup=cancel_keyboard())

@dp.message(Form.waiting_player)
async def player_done(message: types.Message, state: FSMContext):
    user = message.from_user
    await bot.send_message(ADMIN_ID, f"👤 *Жалоба от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
    await message.answer("✅ Отправлено!", reply_markup=main_menu())
    await state.clear()

# ===== ПОДАЧА =====
@dp.message(F.text == "📝 Подача в часть проекта")
async def join_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_join)
    await message.answer(
        "📝 *Анкета*\n\n"
        "1. Возраст:\n2. Часовой пояс:\n3. Юзернейм (@):\n4. Знание правил (1-10):\n"
        "5. Что такое /ban, /mute, /kick?:\n6. Опыт модерации:\n"
        "7. Почему к нам?\n8. Время (часов/день):\n9. О себе:\n\n⏳ 3–7 дней.",
        parse_mode="Markdown", reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_join)
async def join_done(message: types.Message, state: FSMContext):
    user = message.from_user
    await bot.send_message(ADMIN_ID, f"📝 *Заявка от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
    await message.answer("✅ Отправлено!", reply_markup=main_menu())
    await state.clear()

# ===== ВОПРОСЫ =====
@dp.message(F.text == "❓ Вопрос администрации")
async def question_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_question)
    await message.answer("❓ *Вопрос*\n\nЗадайте вопрос одним сообщением.\nМожете приложить скриншоты.", parse_mode="Markdown", reply_markup=cancel_keyboard())

@dp.message(Form.waiting_question)
async def question_done(message: types.Message, state: FSMContext):
    user = message.from_user
    await bot.send_message(ADMIN_ID, f"❓ *Вопрос от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
    await message.answer("✅ Отправлено!", reply_markup=main_menu())
    await state.clear()

async def main():
    # Запускаем веб-сервер ПЕРВЫМ
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web server started on port {PORT}")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
