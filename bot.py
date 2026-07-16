import asyncio 
from aiogram import Bot, Dispatcher, types, F 
from aiogram.filters import Command 
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton 
from aiogram.fsm.context import FSMContext 
from aiogram.fsm.state import State, StatesGroup 
from aiogram.fsm.storage.memory import MemoryStorage 
from aiogram.client.session.aiohttp import AiohttpSession 

API_TOKEN = "8695836578:AAH7LO-Bu6tMXTjvu4yE-Co38Uqkw09TU5Q" 
ADMIN_ID = 7781474535 

session = AiohttpSession(proxy="http://proxy.server:3128") 
bot = Bot(token=API_TOKEN, session=session) 
dp = Dispatcher(storage=MemoryStorage()) 

# --- Константы для кнопок ---
BTN_BUG = "🐛 Баги и дюпы"
BTN_PLAYER = "👤 Жалоба на игрока / КП"
BTN_JOIN = "📝 Подача на часть проекта"
BTN_QUESTION = "❓ Вопрос"
BTN_CANCEL = "🚫 Отмена"

class Form(StatesGroup): 
    waiting_bug = State() 
    waiting_player = State() 
    waiting_join = State() 
    waiting_question = State() 

def main_menu(): 
    kb = [ 
        [KeyboardButton(text=BTN_BUG)], 
        [KeyboardButton(text=BTN_PLAYER)], 
        [KeyboardButton(text=BTN_JOIN)], 
        [KeyboardButton(text=BTN_QUESTION)], 
    ] 
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True) 

def cancel_menu():
    """Клавиатура только с кнопкой Отмена"""
    kb = [[KeyboardButton(text=BTN_CANCEL)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

async def check_state_clean(message: types.Message, state: FSMContext) -> bool:
    """Проверяет, не занят ли пользователь другой формой"""
    current_state = await state.get_state()
    if current_state is not None:
        await message.answer(
            "⚠️ Вы уже заполняете форму.\n"
            "Завершите её или нажмите «🚫 Отмена» для выхода.",
            reply_markup=cancel_menu()
        )
        return False
    return True

# --- /start ---
@dp.message(Command("start")) 
async def start_cmd(message: types.Message, state: FSMContext): 
    await state.clear()
    await message.answer( 
        "🛠 *ColdWorld Support Bot*\n\n" 
        "Выберите раздел:\n" 
        "🐛 Баги и дюпы\n" 
        "👤 Жалоба на игрока / КП\n" 
        "📝 Подача на часть проекта\n" 
        "❓ Вопрос администрации\n\n" 
        "Или просто напишите ваш вопрос.", 
        reply_markup=main_menu(), 
        parse_mode="Markdown" 
    ) 

# --- /cancel + кнопка Отмена ---
@dp.message(Command("cancel"))
@dp.message(F.text == BTN_CANCEL)
async def cancel_action(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("❌ Нет активных действий для отмены.", reply_markup=main_menu())
        return
    await state.clear()
    await message.answer("🚫 Действие отменено.", reply_markup=main_menu())

# --- 🐛 Баги и дюпы ---
@dp.message(F.text == BTN_BUG) 
async def bug_btn(message: types.Message, state: FSMContext): 
    if not await check_state_clean(message, state):
        return
    await message.answer( 
        "🐛 *Баг-репорт*\n\n" 
        "Опишите проблему подробно:\n" 
        "• Никнейм в игре\n" 
        "• Описание бага\n\n" 
        "Приложите скриншот или видео если возможно.\n" 
        "Администрация проверит обращение.\n\n"
        "Для отмены нажмите «🚫 Отмена».", 
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    ) 
    await state.set_state(Form.waiting_bug) 

@dp.message(Form.waiting_bug, ~F.text.startswith("/")) 
async def bug_done(message: types.Message, state: FSMContext): 
    user = message.from_user 
    text = f"🐛 *Баг от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}" 
    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown") 
    await message.answer("✅ Отправлено! Администрация проверит.", reply_markup=main_menu()) 
    await state.clear() 

# --- 👤 Жалоба на игрока / КП ---
@dp.message(F.text == BTN_PLAYER) 
async def player_btn(message: types.Message, state: FSMContext): 
    if not await check_state_clean(message, state):
        return
    await message.answer( 
        "👤 *Жалоба на игрока / КП*\n\n" 
        "Укажите в одном сообщении:\n" 
        "• Никнейм нарушителя\n" 
        "• Что именно произошло\n" 
        "• Доказательства (скриншоты / видео)\n\n" 
        "⚠️ Ложные жалобы наказуемы.\n\n"
        "Для отмены нажмите «🚫 Отмена».", 
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    ) 
    await state.set_state(Form.waiting_player) 

@dp.message(Form.waiting_player, ~F.text.startswith("/")) 
async def player_done(message: types.Message, state: FSMContext): 
    user = message.from_user 
    text = f"👤 *Жалоба от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}" 
    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown") 
    await message.answer("✅ Жалоба отправлена.", reply_markup=main_menu()) 
    await state.clear() 

# --- 📝 Подача на часть проекта ---
@dp.message(F.text == BTN_JOIN) 
async def join_btn(message: types.Message, state: FSMContext): 
    if not await check_state_clean(message, state):
        return
    await message.answer( 
        "📝 *Анкета на часть проекта ColdWorld*\n\n" 
        "Ответьте на все вопросы одним сообщением:\n\n" 
        "1. Возраст:\n" 
        "2. Часовой пояс / страна:\n" 
        "3. Ваш юзернейм в Telegram (@):\n" 
        "4. Знание правил проекта (1-10):\n" 
        "5. Что такое /ban, /mute, /kick? Опишите своими словами:\n" 
        "6. Опыт модерации / администрирования (если есть):\n" 
        "7. Почему хотите присоединиться к команде?\n" 
        "8. Сколько времени готовы уделять (часов в день)?\n" 
        "9. Дополнительная информация о себе:\n\n" 
        "⏳ Рассмотрение: 3–7 дней.\n" 
        "Ответ придёт в этот же чат.\n\n"
        "Для отмены нажмите «🚫 Отмена».", 
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    ) 
    await state.set_state(Form.waiting_join) 

@dp.message(Form.waiting_join, ~F.text.startswith("/")) 
async def join_done(message: types.Message, state: FSMContext): 
    user = message.from_user 
    text = f"📝 *Заявка от* {user.full_name} (@{user.username or 'нет'}, ID: {user.id})\n\n{message.text}" 
    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown") 
    await message.answer("✅ Заявка отправлена! Ответ придёт сюда же.", reply_markup=main_menu()) 
    await state.clear() 

# --- ❓ Вопрос ---
@dp.message(F.text == BTN_QUESTION) 
async def question_btn(message: types.Message, state: FSMContext): 
    if not await check_state_clean(message, state):
        return
    await message.answer( 
        "❓ *Вопрос администрации*\n\n" 
        "Задайте ваш вопрос одним сообщением.\n" 
        "Можете приложить скриншоты.\n\n" 
        "Ответим в ближайшее время!\n\n"
        "Для отмены нажмите «🚫 Отмена».", 
        parse_mode="Markdown",
        reply_markup=cancel_menu()
    ) 
    await state.set_state(Form.waiting_question) 

@dp.message(Form.waiting_question, ~F.text.startswith("/")) 
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
