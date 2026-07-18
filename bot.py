import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = "8695836578:AAH7LO-Bu6tMXTjvu4yE-Co38Uqkw09TU5Q"
ADMIN_ID = 7781474535

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    waiting_bug = State()
    waiting_player = State()
    waiting_join = State()
    waiting_question = State()
    waiting_reply = State()

def main_menu():
    kb = [
        [KeyboardButton(text="🐛 Баги и дюпы")],
        [KeyboardButton(text="👤 Жалоба на игрока / КП")],
        [KeyboardButton(text="📝 Подача на часть проекта")],
        [KeyboardButton(text="❓ Вопрос")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cancel_keyboard():
    kb = [[KeyboardButton(text="🔙 Отмена")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# ===== ОТМЕНА =====
@dp.message(F.text == "🔙 Отмена")
async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer("❌ Действие отменено. Выберите раздел:", reply_markup=main_menu())

# ===== ОТВЕТ ПОЛЬЗОВАТЕЛЮ (ТОЛЬКО АДМИН) =====
@dp.message(Command("reply"))
async def reply_cmd(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Только администратор может отвечать!")
        return
    
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Использование: /reply ID текст\nПример: /reply 7781474535 Привет!")
        return
    
    try:
        user_id = int(args[1])
        reply_text = args[2]
        await bot.send_message(user_id, f"📩 *Ответ от администрации:*\n\n{reply_text}", parse_mode="Markdown")
        await message.answer(f"✅ Ответ отправлен пользователю {user_id}!")
    except:
        await message.answer("❌ Ошибка! Проверьте ID пользователя.")

# ===== СТАРТ =====
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🛠 *ColdWorld Support Bot*\n\n"
        "Выберите раздел:",
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
        "Приложите скриншот или видео.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_bug)
async def bug_done(message: types.Message, state: FSMContext):
    user = message.from_user
    text = f"🐛 *Баг от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}"
    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
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
        "• Доказательства\n\n"
        "⚠️ Ложные жалобы наказуемы.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_player)
async def player_done(message: types.Message, state: FSMContext):
    user = message.from_user
    text = f"👤 *Жалоба от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}"
    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    await message.answer("✅ Жалоба отправлена.", reply_markup=main_menu())
    await state.clear()

# ===== ПОДАЧА =====
@dp.message(F.text == "📝 Подача на часть проекта")
async def join_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_join)
    await message.answer(
        "📝 *Анкета на часть проекта ColdWorld*\n\n"
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
        "⏳ Рассмотрение: 3–7 дней.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_join)
async def join_done(message: types.Message, state: FSMContext):
    user = message.from_user
    text = f"📝 *Заявка от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}"
    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    await message.answer("✅ Заявка отправлена! Ответ придёт сюда же.", reply_markup=main_menu())
    await state.clear()

# ===== ВОПРОСЫ =====
@dp.message(F.text == "❓ Вопрос")
async def question_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_question)
    await message.answer(
        "❓ *Вопрос администрации*\n\n"
        "Задайте ваш вопрос одним сообщением.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

@dp.message(Form.waiting_question)
async def question_done(message: types.Message, state: FSMContext):
    user = message.from_user
    text = f"❓ *Вопрос от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}"
    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    await message.answer("✅ Вопрос отправлен. Ответим в ближайшее время!", reply_markup=main_menu())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
