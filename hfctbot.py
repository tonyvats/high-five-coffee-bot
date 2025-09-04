import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BotCommand
from aiogram import Router
from datetime import datetime, timedelta

API_TOKEN = '8247074222:AAHBww997RhstLFKr3t_MtnRQjU1P_YNfw8'

ADMIN_IDS = [462076, 306535565, 57656547]

syrops = [
    "Кокос", "Лесной орех", "Миндаль", "Фисташка", "Клён-каштан",
    "Бобы тонка", "Ваниль", "Ириска", "Ирландский крем", "Карамель", "Лаванда", "Попкорн",
    "Солёная карамель", "Сгущённое молоко", "Табак-ваниль", "Эвкалипт и мята", "Шоколад",
    "Вишня", "Груша", "Ежевика", "Клубника & земляника", "Малина", "Чёрная смородина",
    "Кашемировый персик", "Яблоко"
]

summer_menu = {
    "Кофе": {
        "Карамельный айс латте со сливочно-солёной пенкой": {"450": 350},
        "Бамбл со свежевыжатым соком": {"350": 390, "450": 440},
        "Эспрессо тоник грейпфрут": {"350": 390, "450": 440},
        "Колдбрю тёмный ром со сливочно-солёной пенкой": {"350": 350}
    },
    "Чай": {
        "Яблочный сорбет матча латте": {"350": 280, "450": 310},
        "Анчан матча латте кокос": {"450": 350},
        "Персиковый чай с ромашкой": {"450": 330}
    },
    "Лимонады": {
        "Лимонад манго-маракуйя": {"450": 330},
        "Лимонад малина-маракуйя": {"450": 330},
        "Лимонад чёрная смородина-мята": {"450": 280},
        "Лимонад черника-мята": {"450": 280}
    }
}

menu = {
    "Чёрный кофе": [
        "Эспрессо двойной", "Американо", "Фильтр", "Колдбрю", "Воронка V60", "Оранж кофе", "Черри фильтр"
    ],
    "Кофе с молоком": [
        "Латте", "Капучино", "Капучино Крим", "Капучино на альтернативном молоке", "Флэт уайт",
        "Ванильный раф", "Горячий шоколад", "Какао", "Пряное какао", "Какао солёная карамель"
    ],
    "SWEET&CRAFT": [
        "Раф инжир и лаванда", "Раф малина и ваниль", "Латте голубика", "Латте абрикос-панела",
        "Наткрекер свит капучино", "Апельсиновый мокко", "Белый шоколад"
    ],
    "Чай": [
        "Чай листовой", "Ройбос с апельсином и мёдом", "Матча латте зелёный", "Анчан матча латте", "Матча на альтернативном молоке"
    ],
    "Детские напитки": [
        "Какао с зефирками", "Детский латте"
    ]
}

sizes = {
    "Эспрессо двойной": ["S"],
    "Американо": ["S", "M", "L"],
    "Фильтр": ["S", "M", "L"],
    "Колдбрю": ["S", "M"],
    "Воронка V60": ["S", "L"],
    "Оранж кофе": ["S", "M", "L"],
    "Черри фильтр": ["S", "M", "L"],
    "Латте": ["M", "L"],
    "Капучино": ["S", "M", "L"],
    "Капучино Крим": ["S", "M", "L"],
    "Капучино на альтернативном молоке": ["S", "M", "L"],
    "Флэт уайт": ["S"],
    "Ванильный раф": ["M", "L"],
    "Горячий шоколад": ["S", "M", "L"],
    "Какао": ["S", "M", "L"],
    "Пряное какао": ["S", "M", "L"],
    "Какао солёная карамель": ["S", "M", "L"],
    "Раф инжир и лаванда": ["M", "L"],
    "Раф малина и ваниль": ["M", "L"],
    "Латте голубика": ["M", "L"],
    "Латте абрикос-панела": ["M", "L"],
    "Наткрекер свит капучино": ["M", "L"],
    "Апельсиновый мокко": ["M", "L"],
    "Белый шоколад": ["M", "L"],
    "Чай листовой": ["M", "L"],
    "Ройбос с апельсином и мёдом": ["M", "L"],
    "Матча латте зелёный": ["S", "M", "L"],
    "Анчан матча латте": ["S", "M", "L"],
    "Матча на альтернативном молоке": ["S", "M", "L"],
    "Какао с зефирками": ["S", "M", "L"],
    "Детский латте": ["S", "M", "L"]
}

prices = {
    "Эспрессо двойной": {"S": 160},
    "Американо": {"S": 180, "M": 210, "L": 240},
    "Фильтр": {"S": 230, "M": 260, "L": 290},
    "Колдбрю": {"S": 250, "M": 270},
    "Воронка V60": {"S": 250, "L": 290},
    "Оранж кофе": {"S": 250, "M": 280, "L": 310},
    "Черри фильтр": {"S": 250, "M": 280, "L": 310},
    "Латте": {"M": 255, "L": 280},
    "Капучино": {"S": 230, "M": 260, "L": 290},
    "Капучино Крим": {"S": 250, "M": 280, "L": 310},
    "Капучино на альтернативном молоке": {"S": 290, "M": 340, "L": 380},
    "Флэт уайт": {"S": 255},
    "Ванильный раф": {"M": 280, "L": 330},
    "Горячий шоколад": {"S": 290, "M": 310, "L": 340},
    "Какао": {"S": 230, "M": 260, "L": 290},
    "Пряное какао": {"S": 240, "M": 270, "L": 300},
    "Какао солёная карамель": {"S": 260, "M": 295, "L": 330},
    "Раф инжир и лаванда": {"M": 280, "L": 320},
    "Раф малина и ваниль": {"M": 290, "L": 330},
    "Латте голубика": {"M": 270, "L": 310},
    "Латте абрикос-панела": {"M": 270, "L": 310},
    "Наткрекер свит капучино": {"M": 310, "L": 350},
    "Апельсиновый мокко": {"M": 290, "L": 330},
    "Белый шоколад": {"M": 280, "L": 320},
    "Чай листовой": {"M": 220, "L": 240},
    "Ройбос с апельсином и мёдом": {"M": 240, "L": 260},
    "Матча латте зелёный": {"S": 240, "M": 260, "L": 280},
    "Анчан матча латте": {"S": 240, "M": 260, "L": 280},
    "Матча на альтернативном молоке": {"S": 300, "M": 340, "L": 370},
    "Какао с зефирками": {"S": 280, "M": 310, "L": 340},
    "Детский латте": {"S": 180, "M": 200, "L": 220},
}

tea_types = [
    "Чёрный с манго", "Зелёный с жасмином", "Эрл грей", "Каркаде вишнёвый",
    "Таёжный с можжевельником", "Белый пион", "Сайган-дайля", "Пу-эр"
]

alt_milk_types = [
    "Овсяное", "Кокосовое", "Фундучное", "Миндальное", "Банановое", "Фисташковое"
]

dopings_full = [
    ("Сироп", 50),
    ("Зефирки", 30),
    ("Мёд", 30),
    ("Доп. эспрессо", 60),
    ("Безлактозное молоко", 40),
    ("Овсяное молоко", 40),
    ("Кокосовое молоко", 40),
    ("Фундучное молоко", 40),
    ("Миндальное молоко", 40),
    ("Банановое молоко", 40),
    ("Фисташковое молоко", 40),
    ("Сахар", 0),
    ("Корица", 0)
]

dopings_names = [d[0] for d in dopings_full]

user_state = {}
router = Router()

BACK_TEXT = "⬅️ Назад"

def back_button():
    return [KeyboardButton(text=BACK_TEXT)]

def start_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сделать заказ")],
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
    user_state[message.from_user.id] = {}
    user_state[message.from_user.id]['step'] = None
    await ask_category(message)

@router.message(lambda message: message.text == "Сделать заказ")
async def handle_make_order(message: types.Message):
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
    await message.answer("Укажи номер телефона или карты постоянного гостя:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
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
        await message.answer("Укажи номер телефона или карты постоянного гостя:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
        user_state[message.from_user.id]['step'] = 'wait_card'
        # История уже содержит правильный предыдущий шаг (wait_size)
        return
    is_alt = drink in ["Капучино на альтернативном молоке", "Матча на альтернативном молоке"]
    kb = []
    for name, price in dopings_full:
        if is_alt and name in alt_milk_types:
            continue
        if is_alt or price == 0:
            btn_text = name
        else:
            btn_text = f"{name} (+{price}₽)"
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

@router.message(lambda message: user_state.get(message.from_user.id, {}).get('step') == 'wait_doping' and (message.text in [f"{d[0]} (+{d[1]}₽)" if d[1] > 0 else d[0] for d in dopings_full] or message.text in [d[0] for d in dopings_full]) and not message.text.startswith("Сироп"))
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
    await message.answer("Укажи номер телефона или карты постоянного гостя:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
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
#     await message.answer("Укажи номер телефона или карты постоянного гостя:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
#     user_state[message.from_user.id]['step'] = 'wait_card'
#     user_state[message.from_user.id]['history'].append('wait_name')

# Временная функция для пропуска шага имени
async def get_name(message: types.Message, bot: Bot, is_back=False):
    # Пропускаем шаг имени, сразу переходим к номеру телефона/карты
    user_state[message.from_user.id]['name'] = "Имя не указано"  # Временное значение
    await message.answer("Укажи номер телефона или карты постоянного гостя:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
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
        await message.answer("Укажи номер телефона или карты постоянного гостя:", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
        user_state[message.from_user.id]['step'] = 'wait_card'
        return
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите только цифры", reply_markup=ReplyKeyboardMarkup(keyboard=[back_button()], resize_keyboard=True))
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
    ready_time = (datetime.now() + timedelta(minutes=minutes, hours=3)).strftime("%H:%M")
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
    if order.get('comment'):
        text += f"\nКомментарий: {order['comment']}"
    # text += f"\nИмя: {order['name']}\nКарта гостя: {order['card']}"
    text += f"\nКарта гостя: {order['card']}"
    text_client = text + f"\nВремя готовности: {ready_time}"
    await message.answer("Спасибо☺️ Заказ принят:\n\n" + text_client, reply_markup=start_menu_keyboard())
    text_admin = text + f"\nЗаберёт через: {order['time']}\nВремя готовности: {ready_time}"
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text_admin)
        except Exception as e:
            print(f"Не удалось отправить заказ {admin_id}: {e}")
    user_state.pop(message.from_user.id, None)
    await ask_category(message)

# --- Обработка любого сообщения вне заказа: всегда показываем меню ---

@router.message()
async def entry_point(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    if user_id not in user_state or user_state[user_id].get('step') is None:
        await ask_category(message)

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.set_my_commands([
        BotCommand(command="start", description="Сделать заказ")
    ])
    
    # Пробуем разные способы запуска
    try:
        # Способ 1: Обычный polling
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"First attempt failed: {e}")
        try:
            # Способ 2: С игнорированием старых сообщений
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(
                bot,
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
        except Exception as e2:
            logging.error(f"Second attempt failed: {e2}")
            try:
                # Способ 3: С таймаутом
                await dp.start_polling(
                    bot,
                    polling_timeout=60,
                    drop_pending_updates=True
                )
            except Exception as e3:
                logging.error(f"All attempts failed: {e3}")
                print("❌ Не удалось запустить бота. Возможно, уже запущен другой экземпляр.")
                print("💡 Попробуйте:")
                print("   1. Остановить другой экземпляр бота")
                print("   2. Создать нового бота через @BotFather")
                print("   3. Подождать несколько минут")

if __name__ == "__main__":
    asyncio.run(main())
