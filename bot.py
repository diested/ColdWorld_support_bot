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
from datetime import datetime

API_TOKEN = "8695836578:AAH7LO-Bu6tMXTjvu4yE-Co38Uqkw09TU5Q"
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
    waiting_ban = State()
    waiting_unban = State()
    waiting_mute = State()

def load_json(file):
    if os.path.exists(file):
        with open(file) as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)

users = set(load_json(USERS_FILE).get("users", []))
bans = load_json(BANS_FILE)
mutes = load_json(MUTES_FILE)

def save_users():
    save_json(USERS_FILE, {"users": list(users)})

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
    kb = [[KeyboardButton(text="🔙 Отмена")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

async def handle_health(request):
    return web.Response(text="OK")

def is_admin(user_id):
    return user_id == ADMIN_ID

def is_banned(user_id):
    return str(user_id) in bans

def is_muted(user_id):
    return str(user_id) in mutes

# ===== ОТМЕНА =====
@dp.message(F.text == "🔙 Отмена")
async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer("❌ Действие отменено.", reply_markup=main_menu())

# ===== ПРОВЕРКА БАНА =====
@dp.message()
async def check_banned(message: types.Message):
    if is_banned(message.from_user.id):
        await message.answer("⛔ Вы забанены в боте.")
        return
    if is_muted(message.from_user.id):
        await message.answer("🤫 Вы замьючены. Сообщение не доставлено.")
        return
    users.add(message.from_user.id)
    save_users()

# ===== РАССЫЛКА =====
@dp.message(Command("broadcast"))
async def broadcast_cmd(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
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

# ===== БАН =====
@dp.message(Command("ban"))
async def ban_cmd(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        await message.answer("❌ /ban ID причина")
        return
    await state.set_state(Form.waiting_ban)
    await state.update_data(ban_id=args[1], reason=args[2] if len(args) > 2 else "Без причины")
    await message.answer(f"Забанить {args[1]}? Напишите `да` для подтверждения.")

@dp.message(Form.waiting_ban)
async def ban_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() != "да":
        await message.answer("❌ Отменено.")
        await state.clear()
        return
    data = await state.get_data()
    bans[data["ban_id"]] = {"reason": data["reason"], "date": datetime.now().isoformat()}
    save_json(BANS_FILE, bans)
    await message.answer(f"✅ Пользователь {data['ban_id']} забанен!")
    await state.clear()

# ===== РАЗБАН =====
@dp.message(Command("unban"))
async def unban_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /unban ID")
        return
    user_id = args[1]
    if user_id in bans:
        del bans[user_id]
        save_json(BANS_FILE, bans)
        await message.answer(f"✅ Пользователь {user_id} разбанен!")
    else:
        await message.answer("❌ Не найден в бане.")

# ===== МЬЮТ =====
@dp.message(Command("mute"))
async def mute_cmd(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        await message.answer("❌ /mute ID причина")
        return
    await state.set_state(Form.waiting_mute)
    await state.update_data(mute_id=args[1], reason=args[2] if len(args) > 2 else "Без причины")
    await message.answer(f"Замьютить {args[1]}? Напишите `да` для подтверждения.")

@dp.message(Form.waiting_mute)
async def mute_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() != "да":
        await message.answer("❌ Отменено.")
        await state.clear()
        return
    data = await state.get_data()
    mutes[data["mute_id"]] = {"reason": data["reason"], "date": datetime.now().isoformat()}
    save_json(MUTES_FILE, mutes)
    await message.answer(f"✅ Пользователь {data['mute_id']} замьючен!")
    await state.clear()

# ===== РАЗМЬЮТ =====
@dp.message(Command("unmute"))
async def unmute_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /unmute ID")
        return
    user_id = args[1]
    if user_id in mutes:
        del mutes[user_id]
        save_json(MUTES_FILE, mutes)
        await message.answer(f"✅ Пользователь {user_id} размьючен!")
    else:
        await message.answer("❌ Не найден в мьюте.")

# ===== БАН-ЛИСТ =====
@dp.message(Command("banlist"))
async def banlist_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    if not bans:
        await message.answer("📋 Бан-лист пуст.")
        return
    text = "📋 *Бан-лист:*\n\n"
    for uid, data in bans.items():
        text += f"• `{uid}` — {data['reason']}\n"
    await message.answer(text, parse_mode="Markdown")

# ===== СТАТИСТИКА =====
@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        f"📊 *Статистика бота:*\n\n"
        f"👥 Пользователей: {len(users)}\n"
        f"🔨 Забанено: {len(bans)}\n"
        f"🤫 Замьючено: {len(mutes)}",
        parse_mode="Markdown"
    )

# ===== ОТВЕТ =====
@dp.message(Command("reply"))
async def reply_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
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

# ===== АДМИН-КОМАНДЫ =====
@dp.message(Command("admin"))
async def admin_help(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "🔧 *Админ-панель ColdWorld:*\n\n"
        "`/ban ID причина` — 🚫 Забанить пользователя\n"
        "`/unban ID` — ✅ Разбанить\n"
        "`/mute ID причина` — 🤫 Замьютить\n"
        "`/unmute ID` — 🔊 Размьютить\n"
        "`/banlist` — 📋 Список забаненных\n"
        "`/stats` — 📊 Статистика бота\n"
        "`/reply ID текст` — 💬 Ответить пользователю\n"
        "`/broadcast` — 📢 Рассылка всем\n"
        "`/admin` — 📖 Эта справка",
        parse_mode="Markdown"
    )

# ===== ПРАВИЛА =====
@dp.message(F.text == "⛄ Правила сервера")
async def rules(message: types.Message):
    kb = [[InlineKeyboardButton(text="📜 Открыть правила", url="https://t.me/coldworld_pravila")]]
    await message.answer("Нажмите кнопку ниже чтобы открыть правила:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

# ===== СТАРТ =====
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

# ===== БАГИ =====
@dp.message(F.text == "🐛 Баги и дюпы")
async def bug_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_bug)
    await message.answer(
        "🐛 *Баг-репорт*\n\n"
        "Опишите проблему подробно:\n"
        "• Никнейм в игре\n"
        "• Описание бага\n\n"
        "Приложите скриншот или видео.\n"
        "Администрация проверит обращение.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_bug)
async def bug_done(message: types.Message, state: FSMContext):
    user = message.from_user
    await bot.send_message(ADMIN_ID, f"🐛 *Баг от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
    await message.answer("✅ Отправлено! Администрация проверит.", reply_markup=main_menu())
    await state.clear()

# ===== ЖАЛОБЫ =====
@dp.message(F.text == "👤 Жалоба на игрока / КП")
async def player_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_player)
    await message.answer(
        "👤 *Жалоба на игрока / КП*\n\n"
        "Укажите в одном сообщении:\n"
        "• Никнейм нарушителя\n"
        "• Что именно произошло\n"
        "• Доказательства (скриншоты / видео)\n\n"
        "⚠️ Ложные жалобы наказуемы.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_player)
async def player_done(message: types.Message, state: FSMContext):
    user = message.from_user
    await bot.send_message(ADMIN_ID, f"👤 *Жалоба от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
    await message.answer("✅ Жалоба отправлена.", reply_markup=main_menu())
    await state.clear()

# ===== ПОДАЧА =====
@dp.message(F.text == "📝 Подача в часть проекта")
async def join_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_join)
    await message.answer(
        "📝 *Анкета в часть проекта ColdWorld*\n\n"
        "Ответьте на все вопросы одним сообщением:\n\n"
        "1. Возраст:\n"
        "2. Часовой пояс / страна:\n"
        "3. Ваш юзернейм в Telegram (@):\n"
        "4. Знание правил проекта (1-10):\n"
        "5. Что такое /ban, /mute, /kick? Опишите:\n"
        "6. Опыт модерации (если есть):\n"
        "7. Почему хотите присоединиться?\n"
        "8. Сколько времени готовы уделять?\n"
        "9. Дополнительная информация:\n\n"
        "⏳ Рассмотрение: 3–7 дней.\n"
        "Ответ придёт в этот же чат.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_join)
async def join_done(message: types.Message, state: FSMContext):
    user = message.from_user
    await bot.send_message(ADMIN_ID, f"📝 *Заявка от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
    await message.answer("✅ Заявка отправлена! Ответ придёт сюда же.", reply_markup=main_menu())
    await state.clear()

# ===== ВОПРОСЫ =====
@dp.message(F.text == "❓ Вопрос администрации")
async def question_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_question)
    await message.answer(
        "❓ *Вопрос администрации*\n\n"
        "Задайте ваш вопрос одним сообщением.\n"
        "Можете приложить скриншоты.\n\n"
        "Ответим в ближайшее время!",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_question)
async def question_done(message: types.Message, state: FSMContext):
    user = message.from_user
    await bot.send_message(ADMIN_ID, f"❓ *Вопрос от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
    await message.answer("✅ Вопрос отправлен. Ответим в ближайшее время!", reply_markup=main_menu())
    await state.clear()

async def main():
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
