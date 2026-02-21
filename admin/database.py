import sqlite3
import os

_DEFAULT_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'menu.db')
DB_PATH = os.environ.get('MENU_DB_PATH', _DEFAULT_DB)


def get_db():
    """Возвращает соединение с БД с включённым foreign_keys."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Создаёт все таблицы, если их ещё нет."""
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS drinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS drink_sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drink_id INTEGER NOT NULL,
            size TEXT NOT NULL,
            price INTEGER NOT NULL,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (drink_id) REFERENCES drinks(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS summer_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS summer_drinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES summer_categories(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS summer_drink_sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drink_id INTEGER NOT NULL,
            size_ml TEXT NOT NULL,
            price INTEGER NOT NULL,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (drink_id) REFERENCES summer_drinks(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS syrups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS dopings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price_s INTEGER NOT NULL DEFAULT 0,
            price_m INTEGER NOT NULL DEFAULT 0,
            price_l INTEGER NOT NULL DEFAULT 0,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS tea_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS alt_milk_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            sort_order INTEGER DEFAULT 0
        );
    ''')
    conn.commit()
    conn.close()


def seed_db():
    """Заполняет БД текущими данными меню (один раз)."""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    if count > 0:
        conn.close()
        return

    cur = conn.cursor()

    # ── Основное меню ──────────────────────────────────────────────
    menu = {
        "Чёрный кофе": [
            "Эспрессо двойной", "Американо", "Фильтр", "Колдбрю",
            "Воронка V60", "Оранж кофе", "Черри фильтр"
        ],
        "Кофе с молоком": [
            "Латте", "Капучино", "Капучино Крим",
            "Капучино на альтернативном молоке", "Флэт уайт",
            "Ванильный раф", "Горячий шоколад", "Какао",
            "Пряное какао", "Какао солёная карамель"
        ],
        "SWEET&CRAFT": [
            "Раф инжир и лаванда", "Раф малина и ваниль",
            "Латте голубика", "Латте абрикос-панела",
            "Наткрекер свит капучино", "Апельсиновый мокко",
            "Белый шоколад"
        ],
        "Чай": [
            "Чай листовой", "Ройбос с апельсином и мёдом",
            "Матча латте зелёный", "Анчан матча латте",
            "Матча на альтернативном молоке"
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
        "Детский латте": ["S", "M", "L"],
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

    size_sort = {"S": 0, "M": 1, "L": 2}

    for cat_idx, (cat_name, drink_list) in enumerate(menu.items()):
        cur.execute(
            "INSERT INTO categories (name, sort_order) VALUES (?, ?)",
            (cat_name, cat_idx),
        )
        cat_id = cur.lastrowid
        for dr_idx, drink_name in enumerate(drink_list):
            cur.execute(
                "INSERT INTO drinks (category_id, name, sort_order) VALUES (?, ?, ?)",
                (cat_id, drink_name, dr_idx),
            )
            drink_id = cur.lastrowid
            for sz in sizes[drink_name]:
                cur.execute(
                    "INSERT INTO drink_sizes (drink_id, size, price, sort_order) VALUES (?, ?, ?, ?)",
                    (drink_id, sz, prices[drink_name][sz], size_sort[sz]),
                )

    # ── Летнее меню ────────────────────────────────────────────────
    summer_menu = {
        "Кофе": {
            "Карамельный айс латте со сливочно-солёной пенкой": {"450": 350},
            "Бамбл со свежевыжатым соком": {"350": 390, "450": 440},
            "Эспрессо тоник грейпфрут": {"350": 390, "450": 440},
            "Колдбрю тёмный ром со сливочно-солёной пенкой": {"350": 350},
        },
        "Чай": {
            "Яблочный сорбет матча латте": {"350": 280, "450": 310},
            "Анчан матча латте кокос": {"450": 350},
            "Персиковый чай с ромашкой": {"450": 330},
        },
        "Лимонады": {
            "Лимонад манго-маракуйя": {"450": 330},
            "Лимонад малина-маракуйя": {"450": 330},
            "Лимонад чёрная смородина-мята": {"450": 280},
            "Лимонад черника-мята": {"450": 280},
        },
    }

    for sc_idx, (sc_name, drinks_dict) in enumerate(summer_menu.items()):
        cur.execute(
            "INSERT INTO summer_categories (name, sort_order) VALUES (?, ?)",
            (sc_name, sc_idx),
        )
        sc_id = cur.lastrowid
        for sd_idx, (sd_name, sizes_prices) in enumerate(drinks_dict.items()):
            cur.execute(
                "INSERT INTO summer_drinks (category_id, name, sort_order) VALUES (?, ?, ?)",
                (sc_id, sd_name, sd_idx),
            )
            sd_id = cur.lastrowid
            for sz_idx, (ml, price) in enumerate(sizes_prices.items()):
                cur.execute(
                    "INSERT INTO summer_drink_sizes (drink_id, size_ml, price, sort_order) VALUES (?, ?, ?, ?)",
                    (sd_id, ml, price, sz_idx),
                )

    # ── Сиропы ─────────────────────────────────────────────────────
    syrops = [
        "Кокос", "Лесной орех", "Миндаль", "Фисташка", "Клён-каштан",
        "Бобы тонка", "Ваниль", "Ириска", "Ирландский крем", "Карамель",
        "Лаванда", "Попкорн", "Солёная карамель", "Сгущённое молоко",
        "Табак-ваниль", "Эвкалипт и мята", "Шоколад", "Вишня", "Груша",
        "Ежевика", "Клубника & земляника", "Малина", "Чёрная смородина",
        "Кашемировый персик", "Яблоко",
    ]
    for i, name in enumerate(syrops):
        cur.execute("INSERT INTO syrups (name, sort_order) VALUES (?, ?)", (name, i))

    # ── Добавки (допинги) ─────────────────────────────────────────
    # (name, price_s, price_m, price_l)
    dopings_data = [
        ("Сироп",              30, 35, 40),
        ("Зефирки",            50, 50, 50),
        ("Мёд",                50, 50, 50),
        ("Доп. эспрессо",      60, 60, 60),
        ("Безлактозное молоко", 30, 30, 30),
        ("Овсяное молоко",     60, 80, 90),
        ("Кокосовое молоко",   60, 80, 90),
        ("Фундучное молоко",   60, 80, 90),
        ("Миндальное молоко",  60, 80, 90),
        ("Банановое молоко",   60, 80, 90),
        ("Фисташковое молоко", 60, 80, 90),
        ("Сахар",               0,  0,  0),
        ("Корица",              0,  0,  0),
    ]
    for i, (name, ps, pm, pl) in enumerate(dopings_data):
        cur.execute(
            "INSERT INTO dopings (name, price_s, price_m, price_l, sort_order) VALUES (?, ?, ?, ?, ?)",
            (name, ps, pm, pl, i),
        )

    # ── Сорта чая ─────────────────────────────────────────────────
    tea_types = [
        "Чёрный с манго", "Зелёный с жасмином", "Эрл грей",
        "Каркаде вишнёвый", "Таёжный с можжевельником",
        "Белый пион", "Сайган-дайля", "Пу-эр",
    ]
    for i, name in enumerate(tea_types):
        cur.execute("INSERT INTO tea_types (name, sort_order) VALUES (?, ?)", (name, i))

    # ── Альтернативное молоко ──────────────────────────────────────
    alt_milk = [
        "Овсяное", "Кокосовое", "Фундучное",
        "Миндальное", "Банановое", "Фисташковое",
    ]
    for i, name in enumerate(alt_milk):
        cur.execute("INSERT INTO alt_milk_types (name, sort_order) VALUES (?, ?)", (name, i))

    conn.commit()
    conn.close()


# ── Функция для получения меню в формате, совместимом с ботом ───
def get_menu_for_bot():
    """
    Возвращает все данные меню в формате словарей,
    совместимом с текущей структурой бота.
    """
    conn = get_db()

    # Основное меню
    menu = {}
    sizes_dict = {}
    prices_dict = {}
    categories = conn.execute("SELECT * FROM categories ORDER BY sort_order").fetchall()
    for cat in categories:
        drinks = conn.execute(
            "SELECT * FROM drinks WHERE category_id = ? ORDER BY sort_order",
            (cat['id'],),
        ).fetchall()
        drink_names = []
        for d in drinks:
            drink_names.append(d['name'])
            ds = conn.execute(
                "SELECT * FROM drink_sizes WHERE drink_id = ? ORDER BY sort_order",
                (d['id'],),
            ).fetchall()
            sizes_dict[d['name']] = [s['size'] for s in ds]
            prices_dict[d['name']] = {s['size']: s['price'] for s in ds}
        menu[cat['name']] = drink_names

    # Летнее меню
    summer_menu = {}
    s_cats = conn.execute("SELECT * FROM summer_categories ORDER BY sort_order").fetchall()
    for sc in s_cats:
        drinks = conn.execute(
            "SELECT * FROM summer_drinks WHERE category_id = ? ORDER BY sort_order",
            (sc['id'],),
        ).fetchall()
        drinks_dict = {}
        for d in drinks:
            ss = conn.execute(
                "SELECT * FROM summer_drink_sizes WHERE drink_id = ? ORDER BY sort_order",
                (d['id'],),
            ).fetchall()
            drinks_dict[d['name']] = {s['size_ml']: s['price'] for s in ss}
        summer_menu[sc['name']] = drinks_dict

    # Сиропы
    syrups = [r['name'] for r in conn.execute("SELECT name FROM syrups ORDER BY sort_order").fetchall()]

    # Добавки
    dopings = []
    for r in conn.execute("SELECT * FROM dopings ORDER BY sort_order").fetchall():
        dopings.append({
            'name': r['name'],
            'price_s': r['price_s'],
            'price_m': r['price_m'],
            'price_l': r['price_l'],
        })

    # Сорта чая
    tea_types = [r['name'] for r in conn.execute("SELECT name FROM tea_types ORDER BY sort_order").fetchall()]

    # Альтернативное молоко
    alt_milk = [r['name'] for r in conn.execute("SELECT name FROM alt_milk_types ORDER BY sort_order").fetchall()]

    conn.close()

    return {
        'menu': menu,
        'sizes': sizes_dict,
        'prices': prices_dict,
        'summer_menu': summer_menu,
        'syrups': syrups,
        'dopings': dopings,
        'tea_types': tea_types,
        'alt_milk_types': alt_milk,
    }
