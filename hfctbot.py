import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton  # WebAppInfo — для WebApp
from aiogram import Router
from datetime import datetime, timedelta, time, timezone

# Добавляем корень проекта в sys.path для импорта admin.database
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from admin.database import get_menu_for_bot, init_db, seed_db

# Загружаем .env — локально переопределяет токен на DEV
load_dotenv()

# Прод-токен по умолчанию. Локально в .env задают BOT_TOKEN с DEV-токеном.
# API_TOKEN = os.environ.get('BOT_TOKEN', '8247074222:AAEKMCOTzGl7QsSE3JmlMLjC1ClbiAkjw30')
from datetime import datetime, timedelta, time

API_TOKEN = '8247074222:AAEKMCOTzGl7QsSE3JmlMLjC1ClbiAkjw30'

# DEV-бот = локальная разработка (время без UTC+3)
RUNNING_LOCAL = '8573322365' in str(API_TOKEN)

ADMIN_IDS = [462076, 306535565, 57656547]
TEAM_CHAT_IDS = [-1002318052349, -2902075036]

# ── Данные меню (загружаются из БД) ────────────────────────────
menu = {}
sizes = {}
prices = {}
summer_menu = {}
syrops = []
dopings_data = []   # [{name, price_s, price_m, price_l}, ...]
dopings_names = []
tea_types = []
alt_milk_types = []


def load_menu():
    """Загружает меню из БД в глобальные переменные."""
    global menu, sizes, prices, summer_menu, syrops
    global dopings_data, dopings_names
    global tea_types, alt_milk_types

    data = get_menu_for_bot()
    menu = data['menu']
    sizes = data['sizes']
    prices = data['prices']
    summer_menu = data['summer_menu']
    syrops = data['syrups']
    tea_types = data['tea_types']
    alt_milk_types = data['alt_milk_types']
    dopings_data = data['dopings']
    dopings_names = [d['name'] for d in dopings_data]


def get_doping_price(name, size='S'):
    """Возвращает цену добавки для указанного размера."""
    for d in dopings_data:
        if d['name'] == name:
            if size == 'L':
                if size == 'L':
                    return d['price_l']
                elif size == 'M':
                    return d['price_m']
                else:
                    return d['price_s']
        return 0


def get_syrup_price(size):
    """Возвращает цену сиропа в зависимости от размера напитка."""
    return get_doping_price('Сироп', size)


def get_alt_milk_price(size):
    """Возвращает цену альтернативного молока в зависимости от размера."""
    for d in dopings_data:
        if d['name'].endswith(' молоко') and d['name'] != 'Безлактозное молоко':
            if size == 'M':
                return d['price_m']
            elif size == 'L':
                return d['price_l']
            return d['price_s']
    return 60  # fallback

def calculate_total_price(order: dict) -> int:
    """Возвращает итоговую стоимость заказа с учётом добавок.

    Основано на финальном состоянии заказа: базовая цена напитка
    (order['price']) плюс стоимость всех выбранных добавок из
    order['dopings'].  Цены добавок зависят от размера напитка.
    """
    base_price = int(order.get('price', 0))
    dopings = order.get('dopings', []) or []
    size = order.get('size', 'S')

    total_extras = 0
    for d in dopings:
        # Сироп приходит как строка вида "Сироп: Ваниль" — считаем по цене "Сироп"
        if isinstance(d, str) and d.startswith("Сироп"):
            total_extras += get_doping_price('Сироп', size)
        else:
            total_extras += get_doping_price(d, size)

    return base_price + total_extras

user_state = {}
router = Router()

# Функция для проверки, является ли чат командным
def is_team_chat(chat_id):
    """Проверяет, является ли чат командным чатом"""
    return chat_id in TEAM_CHAT_IDS

BACK_TEXT = "⬅️ Назад"

def back_button():
    return [KeyboardButton(text=BACK_TEXT)]

def _moscow_now():
    """Текущее время по Москве. Локально — без +3, на сервере — UTC+3."""
    if RUNNING_LOCAL:
        return datetime.now()  # Mac уже в московском времени
    return datetime.now(timezone.utc) + timedelta(hours=3)  # сервер в UTC


def is_working_hours():
    """Проверяет, принимаются ли заказы в текущее время (по Москве)."""
    current_time_only = _moscow_now().time()
    order_start_time = time(9, 50)
    order_end_time = time(21, 30)
    return order_start_time <= current_time_only <= order_end_time

def start_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сделать заказ")],
            # [KeyboardButton(text="🌐 Заказ через WebApp", web_app=WebAppInfo(url="https://curious-swan-008c4e.netlify.app/index.html"))],
        ],
        resize_keyboard=True
    )

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Летнее меню")],
            *[[KeyboardButton(text=cat)] for cat in menu.keys()]
        ],
        resize_keyboard=True
    )

async def ask_category(message: types.Message, is_back=False):
    if user_state.get(message.from_user.id, {}).get('step') is None:
        kb = start_menu_keyboard()
        await message.answer("Привет🖐🏼 Нажми 'Сделать заказ', чтобы начать:", reply_markup=kb)
        user_state[message.from_user.id] = {}
        user_state[message.from_user.id]['step'] = None
        return
    kb = main_menu_keyboard()
    await message.answer("Выбери категорию напитка:", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_category'
    if not is_back:
        user_state[message.from_user.id]['history'] = []

@router.message(Command("start"))
async def start(message: types.Message):
    # Проверяем время работы
    if not is_working_hours():
        await message.answer("Мы работаем с 10:00 до 22:00. Прием заказов с 9:50 до 21:30. Ждем вас в рабочее время! ☕", reply_markup=start_menu_keyboard())
        return
    
    load_menu()  # Обновляем меню из БД при каждом /start
    user_state[message.from_user.id] = {}
    user_state[message.from_user.id]['step'] = None
    await ask_category(message)

@router.message(lambda message: message.text == "Сделать заказ")
async def handle_make_order(message: types.Message):
    # Проверяем время работы
    if not is_working_hours():
        await message.answer("Мы работаем с 10:00 до 22:00. Прием заказов с 9:50 до 21:30. Ждем вас в рабочее время! ☕", reply_markup=start_menu_keyboard())
        return
    
    load_menu()  # Обновляем меню из БД при каждом новом заказе
    user_state[message.from_user.id] = {}
    user_state[message.from_user.id]['step'] = 'wait_category'
    await ask_category(message)

# --- BACK LOGIC ---

@router.message(lambda message: message.text == BACK_TEXT)
async def go_back(message: types.Message, bot: Bot):
    # Приоритетная обработка кнопки "Назад"
    user_id = message.from_user.id
    history = user_state.get(user_id, {}).get('history', [])
    
    if not history:
        await ask_category(message, is_back=True)
        return
    
    prev_step = history.pop()
    user_state[user_id]['step'] = prev_step
    state = user_state[user_id]
    
    # Логируем для отладки
    print(f"User {user_id} going back from {state.get('step')} to {prev_step}")
    
    if prev_step == 'wait_category':
        await ask_category(message, is_back=True)
    elif prev_step == 'wait_summer_type':
        await summer_menu_choose_type(message, is_back=True)
    elif prev_step == 'wait_summer_drink':
        summer_type = state.get('summer_type', list(summer_menu.keys())[0])
        await summer_menu_choose_drink_fake(message, bot, summer_type)
    elif prev_step == 'wait_summer_size':
        summer_type = state.get('summer_type', list(summer_menu.keys())[0])
        drink = state.get('drink', list(summer_menu[summer_type].keys())[0])
        await summer_menu_choose_size_fake(message, bot, summer_type, drink)
    elif prev_step == 'wait_drink':
        category = state.get('category', list(menu.keys())[0])
        await choose_drink_fake(message, bot, category)
    elif prev_step == 'wait_size':
        category = state.get('category', list(menu.keys())[0])
        drink = state.get('drink', list(menu[category])[0])
        await choose_size_fake(message, bot, drink)
    elif prev_step == 'wait_tea_type':
        await check_special(message, bot, is_back=True)
    elif prev_step == 'wait_alt_milk':
        await check_special(message, bot, is_back=True)
    elif prev_step == 'wait_doping':
        await ask_dopings(message, bot, is_back=True)
    elif prev_step == 'wait_syrop':
        await ask_dopings(message, bot, is_back=True)
    # elif prev_step == 'wait_name':
    #     # Возврат со шага имени:
    #     # - Для категории "Кофе с молоком" возвращаемся к выбору добавок
    #     # - Для особых случаев (чай/альтернативное молоко) возвращаемся к их выбору
    #     # - Иначе возвращаемся к выбору размера
    #     category = state.get('category')
    #     drink = state.get('drink')
    #     if category == "Кофе с молоком":
    #         await ask_dopings(message, bot, is_back=True)
    #     elif drink == "Чай листовой" or drink in ["Капучино на альтернативном молоке", "Матча на альтернативном молоке"]:
    #         await check_special(message, bot, is_back=True)
    #     else:
    #         await choose_size_fake(message, bot, drink)
    elif prev_step == 'wait_card':
        # Возврат со шага номера телефона/карты:
        # - Для категории "Кофе с молоком" возвращаемся к выбору добавок
        # - Для особых случаев (чай/альтернативное молоко) возвращаемся к их выбору
        # - Иначе возвращаемся к выбору размера
        category = state.get('category')
        drink = state.get('drink')
        if category == "Кофе с молоком":
            await ask_dopings(message, bot, is_back=True)
        elif drink == "Чай листовой" or drink in ["Капучино на альтернативном молоке", "Матча на альтернативном молоке"]:
            await check_special(message, bot, is_back=True)
        else:
            await choose_size_fake(message, bot, drink)
    elif prev_step == 'wait_time':
        await get_time(message, bot, is_back=True)
    elif prev_step == 'wait_comment':
        await ask_comment(message, bot, is_back=True)
    else:
        await ask_category(message, is_back=True)

# --- FAKE BACK FUNCTIONS ---

async def summer_menu_choose_drink_fake(message, bot, summer_type):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=drink)] for drink in summer_menu[summer_type].keys()] + [back_button()],
        resize_keyboard=True
    )
    await bot.send_message(message.chat.id, "Выбери напиток:", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_summer_drink'

async def summer_menu_choose_size_fake(message, bot, summer_type, drink):
    sizes_prices = summer_menu[summer_type][drink]
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"{size} мл ({price}₽)")] for size, price in sizes_prices.items()] + [back_button()],
        resize_keyboard=True
    )
    await bot.send_message(message.chat.id, "Выбери размер:", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_summer_size'

async def choose_drink_fake(message, bot, category):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=drink)] for drink in menu[category]] + [back_button()],
        resize_keyboard=True
    )
    await bot.send_message(message.chat.id, "Выбери напиток:", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_drink'

async def choose_size_fake(message, bot, drink):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"{s} ({prices[drink][s]}₽)")] for s in sizes[drink]
        ] + [back_button()],
        resize_keyboard=True
    )
    await bot.send_message(message.chat.id, "Выбери размер:", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_size'

# --- SUMMER MENU ---

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_category' and message.text == "Летнее меню")
async def summer_menu_choose_type(message: types.Message, is_back=False):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cat)] for cat in summer_menu.keys()] + [back_button()],
        resize_keyboard=True
    )
    await message.answer("Выбери раздел летнего меню:", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_summer_type'
    if not is_back:
        user_state[message.from_user.id]['history'].append('wait_category')

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_summer_type' and message.text in summer_menu.keys())
async def summer_menu_choose_drink(message: types.Message, is_back=False):
    user_state[message.from_user.id]['summer_type'] = message.text
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=drink)] for drink in summer_menu[message.text].keys()] + [back_button()],
        resize_keyboard=True
    )
    await message.answer("Выбери напиток:", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_summer_drink'
    if not is_back:
        user_state[message.from_user.id]['history'].append('wait_summer_type')

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_summer_drink' and any(message.text in summer_menu[cat] for cat in summer_menu))
async def summer_menu_choose_size(message: types.Message, is_back=False):
    summer_type = user_state[message.from_user.id]['summer_type']
    drink = message.text
    user_state[message.from_user.id]['drink'] = drink
    user_state[message.from_user.id]['summer'] = True
    sizes_prices = summer_menu[summer_type][drink]
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"{size} мл ({price}₽)")] for size, price in sizes_prices.items()] + [back_button()],
        resize_keyboard=True
    )
    await message.answer("Выбери размер:", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_summer_size'
    if not is_back:
        user_state[message.from_user.id]['history'].append('wait_summer_drink')

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_summer_size' and ('мл' in message.text and '(' in message.text))
async def summer_menu_finish_drink(message: types.Message, bot: Bot, is_back=False):
    if message.text == BACK_TEXT:
        await go_back(message, bot)
        return
    size = message.text.split()[0]
    price = int(message.text.split('(')[1].split('₽')[0])
    user_state[message.from_user.id]['size'] = size
    user_state[message.from_user.id]['price'] = price
    # Пропускаем шаг имени, сразу переходим к вводу номера телефона/карты
    user_state[message.from_user.id]['name'] = "Имя не указано"  # Временное значение
    await message.answer("Введите полностью номер телефона:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
    user_state[message.from_user.id]['step'] = 'wait_card'
    if not is_back:
        user_state[message.from_user.id]['history'].append('wait_summer_size')

# --- MAIN MENU ---

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_category' and message.text in menu.keys())
async def choose_drink(message: types.Message, is_back=False):
    user_state[message.from_user.id]['category'] = message.text
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=drink)] for drink in menu[message.text]] + [back_button()],
        resize_keyboard=True
    )
    await message.answer("Выбери напиток:", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_drink'
    if not is_back:
        user_state[message.from_user.id]['history'].append('wait_category')

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_drink' and any(message.text in drinks for drinks in menu.values()))
async def choose_size(message: types.Message, is_back=False):
    user_state[message.from_user.id]['drink'] = message.text
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"{s} ({prices[message.text][s]}₽)")] for s in sizes[message.text]
        ] + [back_button()],
        resize_keyboard=True
    )
    await message.answer("Выбери размер:", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_size'
    if not is_back:
        user_state[message.from_user.id]['history'].append('wait_drink')

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_size' and any(message.text.startswith(s) for s in ["S", "M", "L"]))
async def check_special(message: types.Message, bot: Bot, is_back=False):
    if message.text == BACK_TEXT:
        await go_back(message, bot)
        return
    size = message.text.split()[0]
    user_state[message.from_user.id]['size'] = size
    drink = user_state[message.from_user.id]['drink']
    user_state[message.from_user.id]['price'] = prices[drink][size]
    if drink == "Чай листовой":
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=t)] for t in tea_types] + [back_button()],
            resize_keyboard=True
        )
        await message.answer("Выбери сорт чая:", reply_markup=kb)
        user_state[message.from_user.id]['step'] = 'wait_tea_type'
        if not is_back:
            user_state[message.from_user.id]['history'].append('wait_size')
    elif drink in ["Капучино на альтернативном молоке", "Матча на альтернативном молоке"]:
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=m)] for m in alt_milk_types] + [back_button()],
            resize_keyboard=True
        )
        await message.answer("Выбери альтернативное молоко:", reply_markup=kb)
        user_state[message.from_user.id]['step'] = 'wait_alt_milk'
        if not is_back:
            user_state[message.from_user.id]['history'].append('wait_size')
    else:
        # Для обычных напитков (не чай, не альтернативное молоко) добавляем wait_size в историю
        if not is_back:
            user_state[message.from_user.id]['history'].append('wait_size')
        await ask_dopings(message, bot, is_back=is_back)

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_tea_type' and message.text in tea_types)
async def after_tea_type(message: types.Message, bot: Bot, is_back=False):
    if message.text == BACK_TEXT:
        await go_back(message, bot)
        return
    user_state[message.from_user.id]['tea_type'] = message.text
    await ask_dopings(message, bot, is_back=is_back)

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_alt_milk' and message.text in alt_milk_types)
async def after_alt_milk(message: types.Message, bot: Bot, is_back=False):
    if message.text == BACK_TEXT:
        await go_back(message, bot)
        return
    user_state[message.from_user.id]['alt_milk'] = message.text
    await ask_dopings(message, bot, is_back=is_back)

async def ask_dopings(message, bot: Bot, is_back=False):
    drink = user_state[message.from_user.id]['drink']
    if user_state[message.from_user.id].get('category') != "Кофе с молоком":
        # Для не-молочных напитков сразу переходим к вводу номера телефона/карты
        # НЕ добавляем wait_name в историю, так как этот шаг пропущен
        user_state[message.from_user.id]['name'] = "Имя не указано"  # Временное значение
        await message.answer("Введите полностью номер телефона:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
        user_state[message.from_user.id]['step'] = 'wait_card'
        # История уже содержит правильный предыдущий шаг (wait_size)
        return
    is_alt = drink in ["Капучино на альтернативном молоке", "Матча на альтернативном молоке"]
    size = user_state[message.from_user.id].get('size', 'S')
    kb = []
    for d in dopings_data:
        name = d['name']
        # Для альт. молочных напитков скрываем кнопки альт. молока
        if is_alt and name in [f"{milk} молоко" for milk in alt_milk_types]:
            continue
        price = get_doping_price(name, size)
        if price > 0:
            btn_text = f"{name} (+{price}₽)"
        else:
            btn_text = name
        kb.append([KeyboardButton(text=btn_text)])
    kb.append([KeyboardButton(text="Нет, спасибо")])
    kb.append(back_button())
    await message.answer("Добавить что-нибудь к напитку? (можно выбрать несколько, отправляй по одному, когда закончишь — выбирай 'Нет, спасибо')", reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True))
    user_state[message.from_user.id]['dopings'] = []
    user_state[message.from_user.id]['step'] = 'wait_doping'
    if not is_back:
        user_state[message.from_user.id]['history'].append('wait_size')

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_doping' and message.text.startswith("Сироп"))
async def choose_syrop(message: types.Message, bot: Bot, is_back=False):
    if message.text == BACK_TEXT:
        await go_back(message, bot)
        return
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=s)] for s in syrops] + [[KeyboardButton(text="Нет, спасибо")], back_button()],
        resize_keyboard=True
    )
    await message.answer("Какой сироп добавить?", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_syrop'
    if not is_back:
        user_state[message.from_user.id]['history'].append('wait_doping')

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_syrop' and message.text in syrops)
async def add_syrop(message: types.Message, bot: Bot, is_back=False):
    if message.text == BACK_TEXT:
        await go_back(message, bot)
        return
    user_state[message.from_user.id]['dopings'].append(f"Сироп: {message.text}")
    await ask_dopings(message, bot, is_back=is_back)

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_doping' and not message.text.startswith("Сироп") and message.text.split(" (+")[0] in dopings_names)
async def add_doping(message: types.Message, bot: Bot):
    if message.text == BACK_TEXT:
        await go_back(message, bot)
        return
    name = message.text.split(" (+")[0]
    user_state[message.from_user.id]['dopings'].append(name)
    await message.answer("Добавить ещё что-нибудь? Если нет — выбирай 'Нет, спасибо'.")

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') in ['wait_doping', 'wait_syrop'] and message.text == "Нет, спасибо")
async def finish_order(message: types.Message, bot: Bot):
    # Пропускаем шаг имени, сразу переходим к вводу номера телефона/карты
    user_state[message.from_user.id]['name'] = "Имя не указано"  # Временное значение
    await message.answer("Введите полностью номер телефона:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
    user_state[message.from_user.id]['step'] = 'wait_card'
    # История уже содержит правильный предыдущий шаг

# --- Имя, карта, время, комментарий ---

# @router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_name')
# async def get_name(message: types.Message, bot: Bot, is_back=False):
#     if not is_back and message.text == BACK_TEXT:
#         await go_back(message, bot)
#         return
#     # Если пользователь вернулся на шаг ввода имени — повторно спросим имя и не пойдём дальше
#     if is_back:
#         await message.answer("Напиши своё имя:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
#         user_state[message.from_user.id]['step'] = 'wait_name'
#         return
#     user_state[message.from_user.id]['name'] = message.text
#     await message.answer("Введите полностью номер телефона:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
#     user_state[message.from_user.id]['step'] = 'wait_card'
#     user_state[message.from_user.id]['history'].append('wait_name')

# Временная функция для пропуска шага имени
async def get_name(message: types.Message, bot: Bot, is_back=False):
    # Пропускаем шаг имени, сразу переходим к номеру телефона/карты
    user_state[message.from_user.id]['name'] = "Имя не указано"  # Временное значение
    await message.answer("Введите полностью номер телефона:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
    user_state[message.from_user.id]['step'] = 'wait_card'
    if not is_back:
        # Пропускаем wait_name в истории, не добавляем ничего
        # История уже содержит правильный предыдущий шаг
        pass

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_card')
async def get_card(message: types.Message, bot: Bot, is_back=False):
    if not is_back and message.text == BACK_TEXT:
        await go_back(message, bot)
        return
    # Если вернулись на шаг ввода номера — повторно спросим номер и не пойдём дальше
    if is_back:
        await message.answer("Введите полностью номер телефона:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
        user_state[message.from_user.id]['step'] = 'wait_card'
        return
    # Проверяем, что введены только цифры (11 цифр, начинается с 8 или 7)
    if not message.text.isdigit() or len(message.text) != 11 or not (message.text.startswith('8') or message.text.startswith('7')):
        await message.answer("Пожалуйста, введите номер телефона в формате 89099999999 или 79099999999 (11 цифр, начинается с 8 или 7)", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
        return
    user_state[message.from_user.id]['card'] = message.text
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="10 минут")],
            [KeyboardButton(text="20 минут")],
            [KeyboardButton(text="30 минут")],
            back_button()
        ],
        resize_keyboard=True
    )
    await message.answer("Через сколько минут ты заберёшь свой кофе?", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_time'
    user_state[message.from_user.id]['history'].append('wait_card')

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_time' and "минут" in message.text)
async def get_time(message: types.Message, bot: Bot, is_back=False):
    if not is_back and message.text == BACK_TEXT:
        await go_back(message, bot)
        return
    # Если вернулись на шаг выбора времени — повторно покажем клавиатуру времени и не пойдём дальше
    if is_back:
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="10 минут")],
                [KeyboardButton(text="20 минут")],
                [KeyboardButton(text="30 минут")],
                back_button()
            ],
            resize_keyboard=True
        )
        await message.answer("Через сколько минут ты заберёшь свой кофе?", reply_markup=kb)
        user_state[message.from_user.id]['step'] = 'wait_time'
        return
    user_state[message.from_user.id]['time'] = message.text
    await ask_comment(message, bot, is_back=is_back)
    user_state[message.from_user.id]['history'].append('wait_time')

async def ask_comment(message, bot: Bot, is_back=False):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Далее / пропустить")], back_button()],
        resize_keyboard=True
    )
    await message.answer("Если есть пожелания или комментарии к заказу, напиши их сейчас. Если нет — нажми 'Далее / пропустить'.", reply_markup=kb)
    user_state[message.from_user.id]['step'] = 'wait_comment'
    if not is_back:
        user_state[message.from_user.id]['history'].append('wait_time')

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_comment')
async def get_comment(message: types.Message, bot: Bot, is_back=False):
    if not is_back and message.text == BACK_TEXT:
        await go_back(message, bot)
        return
    if not is_back:
        if message.text != "Далее / пропустить":
            user_state[message.from_user.id]['comment'] = message.text
        else:
            user_state[message.from_user.id]['comment'] = ""
    await send_order(message, bot)

async def send_order(message, bot):
    order = user_state[message.from_user.id]
    minutes = int(order['time'].split()[0])
    ready_time = (_moscow_now() + timedelta(minutes=minutes)).strftime("%H:%M")
    total_price = calculate_total_price(order)
    if order.get('summer'):
        text = f"Летнее меню\nНапиток: {order['drink']}\nРазмер: {order['size']} мл ({order['price']}₽)"
    else:
        text = f"Заказ:\nКатегория: {order.get('category','')}\nНапиток: {order['drink']}\nРазмер: {order['size']} ({order['price']}₽)"
        if 'tea_type' in order:
            text += f"\nСорт чая: {order['tea_type']}"
        if 'alt_milk' in order:
            text += f"\nАльтернативное молоко: {order['alt_milk']}"
        if order.get('dopings'):
            text += f"\nДополнительно: {', '.join(order['dopings'])}"
    # Общая стоимость для всех типов заказов
    text += f"\nИтого: {total_price}₽"
    if order.get('comment'):
        text += f"\nКомментарий: {order['comment']}"
    # text += f"\nИмя: {order['name']}\nКарта гостя: {order['card']}"
    text += f"\nНомер телефона гостя: {order['card']}"
    text_client = text + f"\nВремя готовности: {ready_time}"
    await message.answer("Спасибо☺️ Заказ принят:\n\n" + text_client, reply_markup=start_menu_keyboard())
    text_admin = text + f"\nЗаберёт через: {order['time']}\nВремя готовности: {ready_time}"
    recipient_ids = ADMIN_IDS + TEAM_CHAT_IDS
    for chat_id in recipient_ids:
        try:
            await bot.send_message(chat_id, text_admin)
        except Exception as e:
            print(f"Не удалось отправить заказ {chat_id}: {e}")
    user_state.pop(message.from_user.id, None)
    await ask_category(message)

# --- Обработка любого сообщения вне заказа: всегда показываем меню ---

# @router.message(F.web_app_data)
# async def handle_webapp_data(message: types.Message, bot: Bot):
#     """Обработка данных от WebApp"""
#     try:
#         import json
#         order_data = json.loads(message.web_app_data.data)
#         ...
#     except Exception as e:
#         print(f"Ошибка обработки WebApp данных: {e}")
#         await message.answer("Произошла ошибка при обработке заказа. Попробуйте ещё раз.", reply_markup=start_menu_keyboard())

@router.message()
async def entry_point(message: types.Message, bot: Bot):
    # Если это командный чат - не обрабатываем сообщения (но заказы туда отправляем)
    if is_team_chat(message.chat.id):
        return
    
    # Проверяем время работы для всех сообщений
    if not is_working_hours():
        await message.answer("Мы работаем с 10:00 до 22:00. Прием заказов с 9:50 до 21:30. Ждем вас в рабочее время! ☕", reply_markup=start_menu_keyboard())
        return
    
    user_id = message.from_user.id
    if user_id not in user_state or user_state[user_id].get('step') is None:
        await ask_category(message)
    else:
        # Если пользователь в процессе заказа, но сообщение не обработано другими хендлерами
        await message.answer("Пожалуйста, используйте кнопки для навигации по заказу.", reply_markup=start_menu_keyboard())

async def main():
    logging.basicConfig(level=logging.INFO)

    # Инициализируем БД и загружаем меню
    init_db()
    seed_db()
    load_menu()
    logging.info("Меню загружено из БД (%d категорий, %d напитков)",
                 len(menu), sum(len(v) for v in menu.values()))

    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.set_my_commands([
        BotCommand(command="start", description="Сделать заказ")
    ])

    # Убираем webhook, иначе polling не работает (Conflict)
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Webhook удалён, запуск polling")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
