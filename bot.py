import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
import os

API_TOKEN = "8695836578:AAE7c270zFXF_U3SgmdLrJ3oOTtS4EqN9oQ"
ADMIN_ID = 7781474535
PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    waiting_bug = State()
    waiting_player = State()
    waiting_join = State()
    waiting_media = State()
    waiting_question = State()
    waiting_broadcast = State()

users = {7781474535}
bans = set()
mutes = set()
admins = {7781474535}

def is_admin(uid):
    return uid in admins

def main_menu():
    kb = [
        [KeyboardButton(text="🐛 Баги и дюпы")],
        [KeyboardButton(text="👤 Жалоба на игрока / КП")],
        [KeyboardButton(text="📝 Подача в часть проекта")],
        [KeyboardButton(text="📹 Подача на медиа-творца")],
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
    await message.answer(
        "❄️ *Добро пожаловать в ColdWorld!*\n\n"
        "✨ *Я могу помочь тебе:*\n"
        "• 🐛 Сообщить о багах и дюпах\n"
        "• 👤 Подать жалобу на игрока или КП\n"
        "• 📝 Подать заявку в часть проекта\n"
        "• 📹 Подать заявку на медиа-творца\n"
        "• ❓ Задать вопрос администрации\n"
        "• ⛄ Узнать правила сервера",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "🔙 Отмена")
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=main_menu())

@dp.message(F.text == "⛄ Правила сервера")
async def rules(message: types.Message):
    kb = [[InlineKeyboardButton(text="📜 Открыть правила", url="https://t.me/coldworld_pravila")]]
    await message.answer("Нажмите кнопку ниже чтобы открыть правила сервера:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.message(F.text == "🐛 Баги и дюпы")
async def bug_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_bug)
    await message.answer(
        "🐛 *Баг-репорт*\n\n"
        "Опишите проблему подробно:\n"
        "• Никнейм в игре\n"
        "• Описание бага\n\n"
        "Приложите скриншот или видео если возможно.\n"
        "Администрация проверит обращение.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_bug)
async def bug_done(message: types.Message, state: FSMContext):
    user = message.from_user
    for aid in admins:
        try:
            await bot.send_message(aid, f"🐛 *Баг от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
        except:
            pass
    await message.answer("✅ Отправлено! Администрация проверит.", reply_markup=main_menu())
    await state.clear()

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
    for aid in admins:
        try:
            await bot.send_message(aid, f"👤 *Жалоба от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
        except:
            pass
    await message.answer("✅ Жалоба отправлена.", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text == "📝 Подача в часть проекта")
async def join_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_join)
    await message.answer(
        "📝 *Подача в часть проекта ColdWorld*\n\n"
        "📋 *Критерии для принятия:*\n"
        "• Возраст от 14 лет (исключение для 13)\n"
        "• Знание правил и адекватность\n"
        "• Наличие микрофона\n"
        "• Активность\n\n"
        "📝 *Анкета:*\n"
        "1. Возраст:\n"
        "2. Часовой пояс / страна:\n"
        "3. Ваш юзернейм в Telegram (@):\n"
        "4. Знание правил проекта (1-10):\n"
        "5. Что такое /ban, /mute, /kick? Опишите:\n"
        "6. Опыт модерации (если есть):\n"
        "7. Почему хотите присоединиться?\n"
        "8. Сколько времени готовы уделять?\n\n"
        "⏳ Рассмотрение: 3–7 дней.\n"
        "Ответ придёт в этот же чат.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_join)
async def join_done(message: types.Message, state: FSMContext):
    user = message.from_user
    for aid in admins:
        try:
            await bot.send_message(aid, f"📝 *Заявка в часть проекта от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
        except:
            pass
    await message.answer("✅ Заявка отправлена! Ответ придёт сюда же.", reply_markup=main_menu())
    await state.clear()

@dp.message(F.text == "📹 Подача на медиа-творца")
async def media_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_media)
    await message.answer(
        "📹 *Подача на медиа-творца ColdWorld*\n\n"
        "📋 *Критерии для принятия:*\n"
        "• Возраст от 14 лет (исключение для 13)\n"
        "• Минимум 100 подписчиков\n"
        "• Выход коротких видео раз в 3 дня и длинных раз в неделю\n"
        "• Знание правил и адекватность\n"
        "• Видео не менее 1080p 30fps\n\n"
        "📝 *Анкета:*\n"
        "1. Возраст:\n"
        "2. Часовой пояс / страна:\n"
        "3. Ваш юзернейм в Telegram (@):\n"
        "4. Ссылка на ваш YouTube / TikTok:\n"
        "5. Количество подписчиков:\n"
        "6. Примеры контента:\n\n"
        "⏳ Рассмотрение: 3–7 дней.\n"
        "Ответ придёт в этот же чат.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_media)
async def media_done(message: types.Message, state: FSMContext):
    user = message.from_user
    for aid in admins:
        try:
            await bot.send_message(aid, f"📹 *Заявка на медиа-творца от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
        except:
            pass
    await message.answer("✅ Отправлено!", reply_markup=main_menu())
    await state.clear()

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
    for aid in admins:
        try:
            await bot.send_message(aid, f"❓ *Вопрос от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}", parse_mode="Markdown")
        except:
            pass
    await message.answer("✅ Вопрос отправлен. Ответим в ближайшее время!", reply_markup=main_menu())
    await state.clear()

@dp.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "🔧 *Админ-панель:*\n\n"
        "/addadmin ID — 👑 Добавить\n"
        "/ban ID — 🚫 Бан\n"
        "/unban ID — ✅ Разбан\n"
        "/mute ID — 🤫 Мьют\n"
        "/unmute ID — 🔊 Размьют\n"
        "/banlist — 📋 Баны\n"
        "/stats — 📊 Статистика\n"
        "/reply ID текст — 💬 Ответ\n"
        "/broadcast — 📢 Рассылка",
        parse_mode="Markdown"
    )

@dp.message(Command("addadmin"))
async def addadmin_cmd(message: types.Message, command: CommandObject):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Только главный админ!")
    if not command.args:
        return await message.answer("/addadmin ID")
    try:
        admins.add(int(command.args))
        users.add(int(command.args))
        await message.answer(f"✅ {command.args} теперь админ!")
    except:
        await message.answer("❌ Неверный ID!")

@dp.message(Command("ban"))
async def ban_cmd(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args:
        return await message.answer("/ban ID")
    bans.add(command.args)
    await message.answer(f"✅ {command.args} забанен!")

@dp.message(Command("unban"))
async def unban_cmd(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args:
        return await message.answer("/unban ID")
    bans.discard(command.args)
    await message.answer(f"✅ {command.args} разбанен!")

@dp.message(Command("mute"))
async def mute_cmd(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args:
        return await message.answer("/mute ID")
    mutes.add(command.args)
    await message.answer(f"✅ {command.args} замьючен!")

@dp.message(Command("unmute"))
async def unmute_cmd(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args:
        return await message.answer("/unmute ID")
    mutes.discard(command.args)
    await message.answer(f"✅ {command.args} размьючен!")

@dp.message(Command("banlist"))
async def banlist_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("📋 " + ", ".join(bans) if bans else "📋 Пусто.")

@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(f"👥 {len(users)} | 👑 {len(admins)} | 🔨 {len(bans)} | 🤫 {len(mutes)}")

@dp.message(Command("broadcast"))
async def broadcast_cmd(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(Form.waiting_broadcast)
    await message.answer(f"📢 Введите текст рассылки (получат {len(users)} чел.):")

@dp.message(Form.waiting_broadcast)
async def broadcast_send(message: types.Message, state: FSMContext):
    ok, fail = 0, 0
    for uid in list(users):
        try:
            await bot.send_message(uid, f"📢 *Рассылка ColdWorld:*\n\n{message.text}", parse_mode="Markdown")
            ok += 1
            await asyncio.sleep(0.1)
        except:
            fail += 1
    await message.answer(f"✅ Отправлено: {ok}\n❌ Не доставлено: {fail}", reply_markup=main_menu())
    await state.clear()

@dp.message(Command("reply"))
async def reply_cmd(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id):
        return
    if not command.args:
        return await message.answer("/reply ID текст")
    parts = command.args.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("/reply ID текст")
    try:
        await bot.send_message(int(parts[0]), f"📩 *Ответ администрации:*\n\n{parts[1]}", parse_mode="Markdown")
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
