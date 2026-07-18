import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
import json
import os

API_TOKEN = "8695836578:AAE7c270zFXF_U3SgmdLrJ3oOTtS4EqN9oQ"
ADMIN_ID = 7781474535
USERS_FILE = "users.json"
BANS_FILE = "bans.json"
MUTES_FILE = "mutes.json"
PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    waiting_bug = State()
    waiting_player = State()
    waiting_join = State()
    waiting_question = State()
    waiting_broadcast = State()

users = set()
bans = {}
mutes = {}

if os.path.exists(USERS_FILE):
    with open(USERS_FILE) as f:
        users = set(json.load(f).get("users", []))
if os.path.exists(BANS_FILE):
    with open(BANS_FILE) as f:
        bans = json.load(f)
if os.path.exists(MUTES_FILE):
    with open(MUTES_FILE) as f:
        mutes = json.load(f)

def save_users():
    with open(USERS_FILE, 'w') as f:
        json.dump({"users": list(users)}, f)

def save_bans():
    with open(BANS_FILE, 'w') as f:
        json.dump(bans, f)

def save_mutes():
    with open(MUTES_FILE, 'w') as f:
        json.dump(mutes, f)

def main_menu():
    kb = [
        [KeyboardButton(text="🐛 Баги и дюпы")],
        [KeyboardButton(text="👤 Жалоба на игрока / КП")],
        [KeyboardButton(text="📝 Подача в часть проекта")],
        [KeyboardButton(text="❓ Вопрос администрации")],
        [KeyboardButton(text="⛄ Правила сервера")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cancel_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Отмена")]], resize_keyboard=True)

async def handle_health(request):
    return web.Response(text="OK")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    users.add(message.from_user.id)
    save_users()
    await message.answer(
        "❄️ *Добро пожаловать в ColdWorld!*\n\n"
        "✨ *Я могу помочь тебе:*\n"
        "• 🐛 Сообщить о багах и дюпах\n"
        "• 👤 Подать жалобу на игрока или КП\n"
        "• 📝 Подать заявку в часть проекта\n"
        "• ❓ Задать вопрос администрации\n"
        "• ⛄ Узнать правила сервера",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "🔙 Отмена")
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено.", reply_markup=main_menu())

@dp.message(F.text == "⛄ Правила сервера")
async def rules(message: types.Message):
    kb = [[InlineKeyboardButton(text="📜 Открыть правила", url="https://t.me/coldworld_pravila")]]
    await message.answer("Нажмите кнопку:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.message(F.text == "🐛 Баги и дюпы")
async def bug_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_bug)
    await message.answer("🐛 Опишите баг:", reply_markup=cancel_keyboard())

@dp.message(Form.waiting_bug)
async def bug_done(message: types.Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"🐛 Баг от {message.from_user.full_name} (ID: {message.from_user.id})\n\n{message.text}")
    await message.answer("✅ Отправлено!", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text == "👤 Жалоба на игрока / КП")
async def player_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_player)
    await message.answer("👤 Опишите нарушение:", reply_markup=cancel_keyboard())

@dp.message(Form.waiting_player)
async def player_done(message: types.Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"👤 Жалоба от {message.from_user.full_name} (ID: {message.from_user.id})\n\n{message.text}")
    await message.answer("✅ Отправлено!", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text == "📝 Подача в часть проекта")
async def join_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_join)
    await message.answer("📝 Заполните анкету:\n1. Возраст:\n2. Часовой пояс:\n3. Юзернейм:\n4. Опыт:\n5. Почему к нам?", reply_markup=cancel_keyboard())

@dp.message(Form.waiting_join)
async def join_done(message: types.Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"📝 Заявка от {message.from_user.full_name} (ID: {message.from_user.id})\n\n{message.text}")
    await message.answer("✅ Отправлено!", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text == "❓ Вопрос администрации")
async def question_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_question)
    await message.answer("❓ Задайте вопрос:", reply_markup=cancel_keyboard())

@dp.message(Form.waiting_question)
async def question_done(message: types.Message, state: FSMContext):
    await bot.send_message(ADMIN_ID, f"❓ Вопрос от {message.from_user.full_name} (ID: {message.from_user.id})\n\n{message.text}")
    await message.answer("✅ Отправлено!", reply_markup=main_menu())
    await state.clear()

@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "/ban ID — бан\n/unban ID — разбан\n/mute ID — мьют\n/unmute ID — размьют\n"
        "/banlist — баны\n/stats — статистика\n/reply ID текст — ответ\n/broadcast — рассылка"
    )

@dp.message(Command("ban"))
async def ban_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/ban ID")
        return
    bans[args[1]] = True
    save_bans()
    await message.answer(f"✅ {args[1]} забанен!")

@dp.message(Command("unban"))
async def unban_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/unban ID")
        return
    bans.pop(args[1], None)
    save_bans()
    await message.answer(f"✅ {args[1]} разбанен!")

@dp.message(Command("mute"))
async def mute_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/mute ID")
        return
    mutes[args[1]] = True
    save_mutes()
    await message.answer(f"✅ {args[1]} замьючен!")

@dp.message(Command("unmute"))
async def unmute_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/unmute ID")
        return
    mutes.pop(args[1], None)
    save_mutes()
    await message.answer(f"✅ {args[1]} размьючен!")

@dp.message(Command("banlist"))
async def banlist_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("📋 " + ", ".join(bans.keys()) if bans else "📋 Пусто.")

@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(f"👥 {len(users)} | 🔨 {len(bans)} | 🤫 {len(mutes)}")

@dp.message(Command("broadcast"))
async def broadcast_cmd(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(Form.waiting_broadcast)
    await message.answer("📢 Введите текст:")

@dp.message(Form.waiting_broadcast)
async def broadcast_send(message: types.Message, state: FSMContext):
    for uid in users:
        try:
            await bot.send_message(uid, f"📢 {message.text}")
        except:
            pass
    await message.answer("✅ Отправлено!")
    await state.clear()

@dp.message(Command("reply"))
async def reply_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("/reply ID текст")
        return
    try:
        await bot.send_message(int(args[1]), f"📩 Ответ: {args[2]}")
        await message.answer("✅ Отправлено!")
    except:
        await message.answer("❌ Ошибка!")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
