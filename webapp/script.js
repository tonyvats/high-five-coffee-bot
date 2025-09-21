// Telegram WebApp API
const tg = window.Telegram.WebApp;

// Initialize WebApp
tg.ready();
tg.expand();

// Order data
let order = {
    category: '',
    drink: '',
    size: '',
    price: 0,
    summer: false,
    teaType: '',
    altMilk: '',
    dopings: [],
    phone: '',
    time: '10 минут',
    comment: ''
};

// Menu data (same as in Python)
const summerMenu = {
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
};

const menu = {
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
};

const sizes = {
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
};

const prices = {
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
    "Детский латте": {"S": 180, "M": 200, "L": 220}
};

const teaTypes = [
    "Чёрный с манго", "Зелёный с жасмином", "Эрл грей", "Каркаде вишнёвый",
    "Таёжный с можжевельником", "Белый пион", "Сайган-дайля", "Пу-эр"
];

const altMilkTypes = [
    "Овсяное", "Кокосовое", "Фундучное", "Миндальное", "Банановое", "Фисташковое"
];

// Функция для получения цены альтернативного молока в зависимости от размера
function getAltMilkPrice(size) {
    switch(size) {
        case 'S': return 60;
        case 'M': return 80;
        case 'L': return 90;
        default: return 60;
    }
}

// Функция для получения цены сиропа в зависимости от размера
function getSyrupPrice(size) {
    switch(size) {
        case 'S': return 30;
        case 'M': return 35;
        case 'L': return 40;
        default: return 30;
    }
}


const dopings = [
    { name: "Сироп", price: 0 }, // Динамическая цена
    { name: "Зефирки", price: 50 },
    { name: "Мёд", price: 50 },
    { name: "Доп. эспрессо", price: 60 },
    { name: "Безлактозное молоко", price: 30 },
    { name: "Овсяное молоко", price: 0 }, // Динамическая цена
    { name: "Кокосовое молоко", price: 0 }, // Динамическая цена
    { name: "Фундучное молоко", price: 0 }, // Динамическая цена
    { name: "Миндальное молоко", price: 0 }, // Динамическая цена
    { name: "Банановое молоко", price: 0 }, // Динамическая цена
    { name: "Фисташковое молоко", price: 0 }, // Динамическая цена
    { name: "Сахар", price: 0 },
    { name: "Корица", price: 0 }
];

const syrops = [
    "Кокос", "Лесной орех", "Миндаль", "Фисташка", "Клён-каштан",
    "Бобы тонка", "Ваниль", "Ириска", "Ирландский крем", "Карамель", "Лаванда", "Попкорн",
    "Солёная карамель", "Сгущённое молоко", "Табак-ваниль", "Эвкалипт и мята", "Шоколад",
    "Вишня", "Груша", "Ежевика", "Клубника & земляника", "Малина", "Чёрная смородина",
    "Кашемировый персик", "Яблоко"
];

// Navigation
let currentScreen = 'startScreen';
let screenHistory = [];

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
    currentScreen = screenId;
}

function goBack() {
    if (screenHistory.length > 0) {
        const prevScreen = screenHistory.pop();
        showScreen(prevScreen);
    } else {
        showScreen('startScreen');
    }
}

function navigateTo(screenId) {
    screenHistory.push(currentScreen);
    showScreen(screenId);
}

// Summer menu
function showSummerMenu() {
    navigateTo('summerScreen');
    showSummerCategory('Кофе');
}

function showSummerCategory(category) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Show drinks
    const drinksContainer = document.getElementById('summerDrinks');
    drinksContainer.innerHTML = '';
    
    Object.keys(summerMenu[category]).forEach(drink => {
        const drinkBtn = document.createElement('button');
        drinkBtn.className = 'drink-btn';
        drinkBtn.innerHTML = `
            <h3>${drink}</h3>
            <p>${Object.keys(summerMenu[category][drink]).join(', ')} мл</p>
        `;
        drinkBtn.onclick = () => selectSummerDrink(category, drink);
        drinksContainer.appendChild(drinkBtn);
    });
}

function selectSummerDrink(category, drink) {
    order.category = category;
    order.drink = drink;
    order.summer = true;
    
    // Show size selection
    const sizes = summerMenu[category][drink];
    showSizeSelection(sizes, true);
}

// Regular menu
function showCategory(category) {
    order.category = category;
    order.summer = false;
    document.getElementById('categoryTitle').textContent = category;
    
    const drinksContainer = document.getElementById('drinksList');
    drinksContainer.innerHTML = '';
    
    menu[category].forEach(drink => {
        const drinkBtn = document.createElement('button');
        drinkBtn.className = 'drink-btn';
        drinkBtn.innerHTML = `
            <h3>${drink}</h3>
        `;
        drinkBtn.onclick = () => selectDrink(drink);
        drinksContainer.appendChild(drinkBtn);
    });
    
    navigateTo('categoryScreen');
}

function selectDrink(drink) {
    order.drink = drink;
    
    if (order.summer) {
        const summerSizes = summerMenu[order.category][drink];
        showSizeSelection(summerSizes, true);
    } else {
        const drinkSizes = sizes[drink];
        showSizeSelection(drinkSizes, false);
    }
}

function showSizeSelection(sizesInput, isSummer) {
    document.getElementById('drinkTitle').textContent = order.drink;
    
    const sizeContainer = document.getElementById('sizeOptions');
    sizeContainer.innerHTML = '';
    
    if (isSummer) {
        Object.entries(sizesInput).forEach(([size, price]) => {
            const sizeBtn = document.createElement('button');
            sizeBtn.className = 'size-btn';
            sizeBtn.innerHTML = `
                <div class="size-info">
                    <div class="size-name">${size} мл</div>
                    <div class="size-price">${price}₽</div>
                </div>
            `;
            sizeBtn.onclick = () => selectSize(size, price);
            sizeContainer.appendChild(sizeBtn);
        });
    } else {
        (sizesInput || []).forEach(size => {
            const price = prices[order.drink][size];
            const sizeBtn = document.createElement('button');
            sizeBtn.className = 'size-btn';
            sizeBtn.innerHTML = `
                <div class="size-info">
                    <div class="size-name">${size}</div>
                    <div class="size-price">${price}₽</div>
                </div>
            `;
            sizeBtn.onclick = () => selectSize(size, price);
            sizeContainer.appendChild(sizeBtn);
        });
    }
    
    navigateTo('sizeScreen');
}

function selectSize(size, price) {
    order.size = size;
    order.price = price;
    
    // Check if special options needed
    if (order.drink === 'Чай листовой') {
        showTeaTypes();
    } else if (order.drink === 'Капучино на альтернативном молоке' || order.drink === 'Матча на альтернативном молоке') {
        showAltMilkTypes();
    } else if (order.category === 'Кофе с молоком') {
        showAddons();
    } else {
        showContactForm();
    }
}

function showTeaTypes() {
    document.getElementById('specialTitle').textContent = 'Выберите сорт чая';
    const container = document.getElementById('specialOptions');
    container.innerHTML = '';
    container.className = 'addons-list'; // Используем класс addons-list
    
    teaTypes.forEach(type => {
        const btn = document.createElement('div');
        btn.className = 'addon-item';
        btn.innerHTML = `
            <span class="addon-name">${type}</span>
        `;
        btn.onclick = () => selectTeaType(type);
        container.appendChild(btn);
    });
    
    navigateTo('specialScreen');
}

function selectTeaType(type) {
    // Убираем выделение с предыдущей кнопки
    document.querySelectorAll('.addon-item').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Выделяем текущую кнопку
    event.target.closest('.addon-item').classList.add('selected');
    
    order.teaType = type;
    showAddons();
}

function showAltMilkTypes() {
    document.getElementById('specialTitle').textContent = 'Выберите альтернативное молоко';
    const container = document.getElementById('specialOptions');
    container.innerHTML = '';
    container.className = 'addons-list'; // Используем класс addons-list
    
    altMilkTypes.forEach(type => {
        const btn = document.createElement('div');
        btn.className = 'addon-item';
        btn.innerHTML = `
            <span class="addon-name">${type}</span>
            <span class="addon-price">Бесплатно</span>
        `;
        btn.onclick = () => selectAltMilk(type);
        container.appendChild(btn);
    });
    
    navigateTo('specialScreen');
}

function selectAltMilk(type) {
    // Убираем выделение с предыдущей кнопки
    document.querySelectorAll('.addon-item').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // Выделяем текущую кнопку
    event.target.closest('.addon-item').classList.add('selected');
    
    order.altMilk = type;
    showAddons();
}

function showAddons() {
    const container = document.getElementById('addonsList');
    container.innerHTML = '';
    
    const isAlt = order.drink === 'Капучино на альтернативном молоке' || order.drink === 'Матча на альтернативном молоке';
    const currentSize = order.size;
    
    dopings.forEach(doping => {
        if (isAlt && altMilkTypes.includes(doping.name.replace(' молоко', ''))) {
            return; // Skip alt milk options for alt milk drinks
        }
        
        const item = document.createElement('div');
        item.className = 'addon-item';
        
        // Определяем цену для альтернативного молока и сиропа
        let price = doping.price;
        if (altMilkTypes.includes(doping.name.replace(' молоко', ''))) {
            price = getAltMilkPrice(currentSize);
        } else if (doping.name === 'Сироп') {
            price = getSyrupPrice(currentSize);
        }
        
        // Проверяем, выбрана ли опция
        let isSelected = false;
        if (doping.name === 'Сироп') {
            isSelected = order.dopings.some(d => d.startsWith('Сироп:'));
        } else {
            isSelected = order.dopings.includes(doping.name);
        }
        
        if (isSelected) {
            item.classList.add('selected');
        }
        
        item.innerHTML = `
            <span class="addon-name">${doping.name}</span>
            <span class="addon-price">${price > 0 ? `+${price}₽` : 'Бесплатно'}</span>
        `;
        item.onclick = () => {
            if (doping.name === 'Сироп') {
                showSyropFlavors();
                return;
            }
            toggleAddon(doping, item, price);
        };
        container.appendChild(item);
    });
    
    navigateTo('addonsScreen');
}

function toggleAddon(doping, element, price) {
    if (element.classList.contains('selected')) {
        element.classList.remove('selected');
        // Для сиропа нужно найти и удалить правильный элемент
        if (doping.name === 'Сироп') {
            order.dopings = order.dopings.filter(d => !d.startsWith('Сироп:'));
        } else {
            order.dopings = order.dopings.filter(d => d !== doping.name);
        }
    } else {
        element.classList.add('selected');
        order.dopings.push(doping.name);
    }
    updateOrderInfo();
}

function finishAddons() {
    showContactForm();
}

// Syrup selection
function showSyropFlavors() {
    const list = document.getElementById('syropList');
    list.innerHTML = '';
    syrops.forEach(flavor => {
        const item = document.createElement('div');
        item.className = 'addon-item';
        item.innerHTML = `
            <span class="addon-name">${flavor}</span>
        `;
        item.onclick = () => {
            const fullName = `Сироп: ${flavor}`;
            if (!order.dopings.includes(fullName)) {
                order.dopings.push(fullName);
            }
            // вернуться к списку добавок
            navigateTo('addonsScreen');
            updateOrderInfo();
        };
        list.appendChild(item);
    });
    navigateTo('syropScreen');
}

function showContactForm() {
    navigateTo('contactScreen');
}

function updateOrderInfo() {
    const orderInfo = document.getElementById('orderInfo');
    const orderSummary = document.getElementById('orderSummary');
    const orderPrice = document.getElementById('orderPrice');
    
    if (order.drink) {
        let summary = order.drink;
        if (order.size) {
            summary += ` (${order.size}${order.summer ? ' мл' : ''})`;
        }
        if (order.teaType) {
            summary += ` - ${order.teaType}`;
        }
        if (order.altMilk) {
            summary += ` - ${order.altMilk}`;
        }
        if (order.dopings.length > 0) {
            summary += ` + ${order.dopings.join(', ')}`;
        }
        
        orderSummary.textContent = summary;
        orderPrice.textContent = `${calculateTotalPrice()}₽`;
        orderInfo.style.display = 'flex';
    } else {
        orderInfo.style.display = 'none';
    }
}

function calculateTotalPrice() {
    let total = order.price || 0;
    order.dopings.forEach(dopingName => {
        // Сироп приходит как строка вида "Сироп: Ваниль" — считаем по цене "Сироп"
        if (dopingName.startsWith("Сироп")) {
            total += getSyrupPrice(order.size);
        } else {
            const doping = dopings.find(d => d.name === dopingName);
            if (doping) {
                // Для альтернативного молока используем динамическую цену
                if (altMilkTypes.includes(dopingName.replace(' молоко', ''))) {
                    total += getAltMilkPrice(order.size);
                } else {
                    total += doping.price;
                }
            }
        }
    });
    return total;
}

function submitOrder() {
    const phone = document.getElementById('phone').value;
    const time = document.getElementById('time').value;
    const comment = document.getElementById('comment').value;
    
    if (!phone || phone.length !== 11 || (!phone.startsWith('8') && !phone.startsWith('7'))) {
        alert('Пожалуйста, введите корректный номер телефона (11 цифр, начинается с 8 или 7)');
        return;
    }
    
    order.phone = phone;
    order.time = time;
    order.comment = comment;
    
    // Send order to bot
    tg.sendData(JSON.stringify(order));
    tg.close();
}

// Initialize
updateOrderInfo();
