# 🚀 БЮДЖЕТНАЯ архитектура парсинга автосайтов

**Версия:** 2.0 (оптимизированная)
**Цель:** Максимальное удешевление без потери качества
**Экономия:** ~$6,500/год ($540/мес → $140-200/мес)

---

## 📊 Сравнение версий

| Компонент | Версия 1.0 | Версия 2.0 (Budget) | Экономия |
|-----------|------------|---------------------|----------|
| **СУБД** | PostgreSQL | SQLite | -$15/мес |
| **Сервер** | VPS $25 | Локально (ПК пользователя) | -$25/мес |
| **Хранение** | Cloud/SSD | Локальный HDD | -$10/мес |
| **Прокси Residential** | 20GB ($120-160) | 10GB ($80-100) | -$60/мес |
| **Прокси Mobile** | 5GB ($50-75) | 2GB ($30-50) | -$25/мес |
| **Перевод** | DeepL полный ($200-500) | Словари + заголовки ($30-50) | -$450/мес |
| **Итого** | **$405-780/мес** | **$140-200/мес** | **~$540/мес** |

---

## 🏗️ Новая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                    БЮДЖЕТНАЯ СИСТЕМА                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   che168.com │    │ dongchedi.com│    │   encar.com  │      │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             ▼                                   │
│         ┌─────────────────────────────────────┐                 │
│         │      MINIMAL PROXY LAYER            │                 │
│         │  - Residential 10GB (основа)        │                 │
│         │  - Mobile 2GB (только Encar)        │                 │
│         └─────────────────────────────────────┘                 │
│                             │                                   │
│         ┌───────────────────▼───────────────────┐               │
│         │         PARSER ENGINE                 │               │
│         │  - Python + aiohttp (легковесный)    │               │
│         │  - Playwright (только для Encar)     │               │
│         │  - Rate Limiter + Retry              │               │
│         └─────────────────────────────────────┘                 │
│                             │                                   │
│         ┌───────────────────▼───────────────────┐               │
│         │      TRANSLATION LITE                 │               │
│         │  ┌─────────────────────────────────┐  │               │
│         │  │ 1. Словари (авто-термины)       │  │               │
│         │  │    - 500-1000 уникальных значений │ │               │
│         │  │    - Переводятся 1 раз навсегда  │  │               │
│         │  │ 2. Заголовки (короткие)         │  │               │
│         │  │    - DeepL API минимально        │  │               │
│         │  │ 3. Описания                     │  │               │
│         │  │    - НЕ переводятся              │  │               │
│         │  └─────────────────────────────────┘  │               │
│         └─────────────────────────────────────┘                 │
│                             │                                   │
│         ┌───────────────────▼───────────────────┐               │
│         │        SQLite Database                │               │
│         │  ┌─────────────────────────────────┐  │               │
│         │  │  Файл: C:\Data\autos.db         │  │               │
│         │  │  Размер: ~500MB для 1M записей  │  │               │
│         │  │  Хранение: обычный HDD          │  │               │
│         │  └─────────────────────────────────┘  │               │
│         └─────────────────────────────────────┘                 │
│                             │                                   │
│         ┌───────────────────▼───────────────────┐               │
│         │         EXPORT SERVICE                │               │
│         │  - JSON files (для сайта)             │               │
│         │  - Прямой доступ к SQLite с сайта     │               │
│         └─────────────────────────────────────┘                 │
│                             │                                   │
│                             ▼                                   │
│                    ┌─────────────────┐                          │
│                    │   ВАШ САЙТ      │                          │
│                    └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💾 1. Хранение данных (SQLite + HDD)

### Почему SQLite?

| Критерий | PostgreSQL | SQLite |
|----------|------------|--------|
| Производительность 1M записей | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Простота настройки | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Требования к ресурсам | 2-4GB RAM | 100MB RAM |
| Администрирование | Требуется опыт | Не требуется |
| Стоимость | $0-30/мес | $0 |
| Надежность | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Бенчмарки SQLite с 1M записей:**
- SELECT по индексу: <10ms
- INSERT пакетом 1000: ~100ms
- UPDATE по индексу: <5ms

### Схема SQLite (упрощенная)

```sql
-- Справочник марок и моделей (переводится 1 раз)
CREATE TABLE car_makes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_original TEXT NOT NULL,      -- BMW, Mercedes
    name_ru TEXT NOT NULL,            -- БМВ, Мерседес
    UNIQUE(name_original)
);

CREATE TABLE car_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make_id INTEGER REFERENCES car_makes(id),
    name_original TEXT NOT NULL,      -- 5 Series, E-Class
    name_ru TEXT NOT NULL,            -- 5 Серия, E-Класс
    UNIQUE(make_id, name_original)
);

-- Справочник характеристик (переводится 1 раз)
CREATE TABLE ref_transmission (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE,      -- AT, MT, AMT
    name_cn TEXT,          -- 自动挡
    name_ko TEXT,          -- 자동변속기
    name_ru TEXT           -- АКПП
);

CREATE TABLE ref_fuel_type (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE,
    name_cn TEXT,
    name_ko TEXT,
    name_ru TEXT
);

CREATE TABLE ref_drive_type (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE,
    name_cn TEXT,
    name_ko TEXT,
    name_ru TEXT
);

CREATE TABLE ref_body_type (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE,
    name_cn TEXT,
    name_ko TEXT,
    name_ru TEXT
);

CREATE TABLE ref_color (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE,
    name_cn TEXT,
    name_ko TEXT,
    name_ru TEXT
);

-- Основная таблица (минимум текста для перевода)
CREATE TABLE listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_site TEXT NOT NULL,         -- che168, dongchedi, encar
    external_id TEXT NOT NULL,         -- ID на сайте
    url TEXT NOT NULL,

    -- Ссылки на справочники (вместо текста)
    make_id INTEGER REFERENCES car_makes(id),
    model_id INTEGER REFERENCES car_models(id),
    transmission_id INTEGER REFERENCES ref_transmission(id),
    fuel_type_id INTEGER REFERENCES ref_fuel_type(id),
    drive_type_id INTEGER REFERENCES ref_drive_type(id),
    body_type_id INTEGER REFERENCES ref_body_type(id),
    color_id INTEGER REFERENCES ref_color(id),

    -- Числовые данные (не переводятся)
    year INTEGER NOT NULL,
    mileage INTEGER,
    engine_volume REAL,
    engine_power INTEGER,
    doors INTEGER,

    -- Цены
    price_original REAL NOT NULL,
    currency_original TEXT NOT NULL,   -- CNY, KRW
    price_usd REAL,
    price_rub REAL,

    -- Только заголовок для перевода (короткий)
    title_short TEXT,                  -- "BMW 5 Series 2022, 35000 км"

    -- Описание НЕ переводится!
    description_original TEXT,         -- Оригинальное описание (опционально)

    -- Метаданные
    images_json TEXT,                  -- JSON массив URL
    location TEXT,
    seller_info TEXT,

    -- Статусы
    status TEXT DEFAULT 'active',      -- active, sold, archived
    is_exported INTEGER DEFAULT 0,

    -- Временные метки
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(source_site, external_id)
);

-- Индексы для производительности
CREATE INDEX idx_listings_make ON listings (make_id);
CREATE INDEX idx_listings_model ON listings (model_id);
CREATE INDEX idx_listings_year ON listings (year);
CREATE INDEX idx_listings_price ON listings (price_usd);
CREATE INDEX idx_listings_status ON listings (status);
CREATE INDEX idx_listings_created ON listings (created_at);
CREATE INDEX idx_listings_source ON listings (source_site);

-- Таблица сайтов
CREATE TABLE source_sites (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT NOT NULL,
    language TEXT,                   -- zh, ko
    parse_interval_hours INTEGER,    -- 4, 6
    last_parse_at TIMESTAMP
);

-- Таблица валют (обновляется вручную/скриптом)
CREATE TABLE currency_rates (
    id INTEGER PRIMARY KEY,
    currency_code TEXT UNIQUE,       -- CNY, KRW, USD
    rate_to_usd REAL,
    rate_to_rub REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Начальные данные
INSERT INTO source_sites (name, domain, language, parse_interval_hours) VALUES
('Che168', 'che168.com', 'zh', 4),
('Dongchedi', 'dongchedi.com', 'zh', 4),
('Encar', 'encar.com', 'ko', 6);

INSERT INTO currency_rates (currency_code, rate_to_usd, rate_to_rub) VALUES
('CNY', 0.137, 12.5),    -- 1 CNY = 0.137 USD = 12.5 RUB
('KRW', 0.00071, 0.065),  -- 1 KRW = 0.00071 USD
('USD', 1.0, 91.0);       -- 1 USD = 91 RUB
```

### Структура хранения на диске

```
C:\Data\Autos\
├── autos.db                    # SQLite база (~500MB для 1M записей)
├── autos.db-shm                # Shared memory (автоматически)
├── autos.db-wal                # Write-ahead log (автоматически)
│
├── images\                     # Кэшированные изображения (опционально)
│   ├── che168\
│   ├── dongchedi\
│   └── encar\
│
├── export\                     # Экспортированные файлы
│   ├── listings_2025-03-25.json
│   └── ...
│
└── backups\                    # Ежедневные бэкапы
    ├── autos_2025-03-24.db
    └── ...
```

**Размер базы:**
- 1 запись ≈ 500 байт
- 1,000,000 записей ≈ 500 MB
- С индексами ≈ 700-800 MB
- **Обычного HDD на 500GB+ хватит на годы**

---

## 🌐 2. Перевод (максимальная экономия)

### Стратегия "Словари + минимум API"

```
┌─────────────────────────────────────────────────────────────┐
│              СТРАТЕГИЯ ПЕРЕВОДА v2.0                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. СПРАВОЧНИКИ (переводится 1 раз навсегда)                │
│     ┌─────────────────────────────────────────────────────┐ │
│     │ Марки авто: BMW, Mercedes, Audi... ~50 шт.          │ │
│     │ Модели: 5 Series, E-Class, A6... ~500 шт.           │ │
│     │ Типы КПП: AT, MT, AMT, CVT... ~10 шт.               │ │
│     │ Типы топлива: Gasoline, Diesel, EV, Hybrid... ~10   │ │
│     │ Привод: FWD, RWD, AWD, 4WD... ~10 шт.               │ │
│     │ Кузов: Sedan, SUV, Wagon, Coupe... ~20 шт.          │ │
│     │ Цвета: White, Black, Silver... ~30 шт.              │ │
│     └─────────────────────────────────────────────────────┘ │
│     Итого: ~600-700 уникальных значений                     │
│     Перевод: DeepL 1 раз (~$5-10) или вручную               │
│     Далее: БЕСПЛАТНО (подстановка по ID)                    │
│                                                             │
│  2. ЗАГОЛОВКИ (короткие, ~50 символов)                      │
│     ┌─────────────────────────────────────────────────────┐ │
│     │ Формат: "BMW 5 Series 2022, 35000 км"               │ │
│     │ Генерируется автоматически из справочников!         │ │
│     │ НЕ ТРЕБУЕТ перевода!                                │ │
│     └─────────────────────────────────────────────────────┘ │
│     Итого: $0 (автогенерация)                               │
│                                                             │
│  3. ОПИСАНИЯ (длинные тексты)                               │
│     ┌─────────────────────────────────────────────────────┐ │
│     │ Решение: НЕ переводить вообще!                      │ │
│     │ Покупатель смотрит на фото и характеристики         │ │
│     │ Описание — вторично                                 │ │
│     └─────────────────────────────────────────────────────┘ │
│     Итого: $0 (полная экономия)                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Словари терминов (готовые данные)

```json
// data/dictionaries/zh_ru.json
{
  "transmission": {
    "自动挡": {"code": "AT", "ru": "АКПП"},
    "手动挡": {"code": "MT", "ru": "МКПП"},
    "手自一体": {"code": "AMT", "ru": "Робот"},
    "无级变速": {"code": "CVT", "ru": "Вариатор"}
  },
  "fuel_type": {
    "汽油": {"code": "GAS", "ru": "Бензин"},
    "柴油": {"code": "DSL", "ru": "Дизель"},
    "纯电动": {"code": "EV", "ru": "Электро"},
    "混合动力": {"code": "HYB", "ru": "Гибрид"},
    "插电混动": {"code": "PHEV", "ru": "Плагин-гибрид"}
  },
  "drive_type": {
    "前置前驱": {"code": "FWD", "ru": "Передний"},
    "前置后驱": {"code": "RWD", "ru": "Задний"},
    "前置四驱": {"code": "AWD", "ru": "Полный"},
    "四驱": {"code": "4WD", "ru": "4WD"}
  },
  "body_type": {
    "轿车": {"code": "SED", "ru": "Седан"},
    "SUV": {"code": "SUV", "ru": "Внедорожник"},
    "MPV": {"code": "MPV", "ru": "Минивэн"},
    "跑车": {"code": "CP", "ru": "Купе"},
    "敞篷": {"code": "CB", "ru": "Кабриолет"},
    "旅行车": {"code": "WGN", "ru": "Универсал"},
    "两厢": {"code": "HB", "ru": "Хэтчбек"}
  },
  "color": {
    "白色": {"code": "WHT", "ru": "Белый"},
    "黑色": {"code": "BLK", "ru": "Черный"},
    "灰色": {"code": "GRY", "ru": "Серый"},
    "银色": {"code": "SLV", "ru": "Серебристый"},
    "红色": {"code": "RED", "ru": "Красный"},
    "蓝色": {"code": "BLU", "ru": "Синий"},
    "棕色": {"code": "BRN", "ru": "Коричневый"},
    "金色": {"code": "GLD", "ru": "Золотой"}
  }
}
```

```json
// data/dictionaries/ko_ru.json
{
  "transmission": {
    "자동변속기": {"code": "AT", "ru": "АКПП"},
    "수동변속기": {"code": "MT", "ru": "МКПП"},
    "자동수동": {"code": "AMT", "ru": "Робот"},
    "무단변속기": {"code": "CVT", "ru": "Вариатор"}
  },
  "fuel_type": {
    "가솔린": {"code": "GAS", "ru": "Бензин"},
    "디젤": {"code": "DSL", "ru": "Дизель"},
    "전기": {"code": "EV", "ru": "Электро"},
    "하이브리드": {"code": "HYB", "ru": "Гибрид"},
    "플러그인하이브리드": {"code": "PHEV", "ru": "Плагин-гибрид"}
  },
  "drive_type": {
    "전륜구동": {"code": "FWD", "ru": "Передний"},
    "후륜구동": {"code": "RWD", "ru": "Задний"},
    "사륜구동": {"code": "AWD", "ru": "Полный"},
    "4륜구동": {"code": "4WD", "ru": "4WD"}
  },
  "body_type": {
    "세단": {"code": "SED", "ru": "Седан"},
    "SUV": {"code": "SUV", "ru": "Внедорожник"},
    "미니밴": {"code": "MPV", "ru": "Минивэн"},
    "쿠페": {"code": "CP", "ru": "Купе"},
    "컨버터블": {"code": "CB", "ru": "Кабриолет"},
    "왜건": {"code": "WGN", "ru": "Универсал"},
    "해치백": {"code": "HB", "ru": "Хэтчбек"}
  },
  "color": {
    "흰색": {"code": "WHT", "ru": "Белый"},
    "검은색": {"code": "BLK", "ru": "Черный"},
    "회색": {"code": "GRY", "ru": "Серый"},
    "은색": {"code": "SLV", "ru": "Серебристый"},
    "빨간색": {"code": "RED", "ru": "Красный"},
    "파란색": {"code": "BLU", "ru": "Синий"},
    "갈색": {"code": "BRN", "ru": "Коричневый"}
  }
}
```

### Генерация заголовка (без перевода!)

```python
def generate_title_ru(listing):
    """
    Автогенерация заголовка на русском из справочников.
    НЕТ переводу API!
    """
    # make_ru = "BMW" (из справочника, не переводится)
    # model_ru = "5 Серия" (из справочника, переведено 1 раз)
    # year = 2022
    # mileage = 35000

    title = f"{listing['make_ru']} {listing['model_ru']} {listing['year']}, {listing['mileage']} км"
    return title

# Пример результата:
# "BMW 5 Серия 2022, 35000 км"
# "Hyundai Sonata 2021, 48000 км"
```

### Расчет стоимости перевода

| Статья | Версия 1.0 | Версия 2.0 | Экономия |
|--------|------------|------------|----------|
| Справочники (1 раз) | $0 | $5-10 | -$10 |
| Заголовки (ежемес) | $100-200 | $0 | -$200 |
| Описания (ежемес) | $100-300 | $0 | -$300 |
| **Итого в месяц** | **$200-500** | **$0** (после 1 раза) | **-$500** |

**Перевод справочников:**
- ~700 уникальных значений × 50 символов = 35,000 символов
- DeepL: 35,000 / 1,000,000 × $20 = **$0.70** (один раз!)

---

## 🔌 3. Прокси (оптимизация)

### Новая стратегия

| Сайт | Прокси | Трафик/мес | Цена |
|------|--------|------------|------|
| che168.com | Residential | 4GB | $30 |
| dongchedi.com | Residential | 4GB | $30 |
| encar.com | Mobile | 2GB | $40-50 |
| **Итого** | | **10GB** | **$100-110** |

### Почему дешевле?

1. **Меньше трафика** — парсим только основные страницы, без лишних запросов
2. **Умное кэширование** — не парсим одно и то же дважды
3. **Только mobile для Encar** — он самый строгий, остальные дешевле

### Рекомендуемые провайдеры (бюджет)

| Провайдер | Тип | Цена/GB | Мин. покупка |
|-----------|-----|---------|--------------|
| **Smartproxy** | Residential | $6-8 | 5GB = $40 |
| **IPRoyal** | Residential | $4-6 | 5GB = $25 |
| **Bright Data** | Mobile | $20/GB | 2GB = $40 |

---

## 💻 4. Локальный запуск (без VPS)

### Преимущества

- ✅ $0 за сервер
- ✅ Полный доступ к железу
- ✅ Нет задержек на сеть
- ✅ Легче отладка

### Требования к ПК

| Компонент | Минимум | Рекомендую |
|-----------|---------|------------|
| CPU | 4 ядра | 6+ ядер |
| RAM | 8GB | 16GB |
| Disk | 100GB HDD | 500GB HDD |
| Internet | 50 Mbps | 100+ Mbps |

### Структура проекта (локальная)

```
C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\
├── src\
│   ├── main.py                 # Точка входа
│   ├── config.py               # Настройки
│   │
│   ├── parsers\
│   │   ├── base_parser.py      # Базовый класс
│   │   ├── che168_parser.py    # aiohttp (быстро)
│   │   ├── dongchedi_parser.py # aiohttp (быстро)
│   │   └── encar_parser.py     # Playwright (сложнее)
│   │
│   ├── proxy\
│   │   ├── manager.py          # Ротация прокси
│   │   └── providers.py        # Провайдеры
│   │
│   ├── database\
│   │   ├── sqlite_db.py        # SQLite подключение
│   │   ├── repositories.py     # Репозитории
│   │   └── dictionaries.py     # Словари
│   │
│   ├── translation\
│   │   ├── dictionary_loader.py # Загрузка словарей
│   │   └── title_generator.py  # Генерация заголовков
│   │
│   ├── export\
│   │   ├── json_exporter.py    # Экспорт в JSON
│   │   └── scheduler.py        # Расписание
│   │
│   └── utils\
│       ├── logging.py          # Логи в файл
│       └── currency.py         # Курсы валют (без API)
│
├── data\
│   ├── dictionaries\
│   │   ├── zh_ru.json          # Китай → Русский
│   │   └── ko_ru.json          # Корея → Русский
│   │
│   └── backups\                # Бэкапы БД
│
├── C:\Data\Autos\
│   ├── autos.db                # Основная БД
│   ├── images\                 # Фото (опционально)
│   └── export\                 # Экспорт файлы
│
├── .env
├── requirements.txt
└── run.bat                     # Запуск в 1 клик
```

### requirements.txt (минимум)

```
aiohttp>=3.9.0          # Асинхронные HTTP запросы
playwright>=1.40.0      # Только для Encar
aiosqlite>=0.19.0       # Async SQLite
python-dotenv>=1.0.0    # .env файлы
schedule>=1.2.0         # Расписание
```

**Итого:** ~5 основных пакетов (против 15+ в версии 1.0)

---

## 💱 5. Калькулятор валют (без API)

### Простое решение

```python
# utils/currency.py

# Курсы обновляются вручную раз в неделю/месяц
# Источники: cbr.ru, xe.com (бесплатно)

CURRENCY_RATES = {
    'CNY': {'usd': 0.137, 'rub': 12.5},   # 1 CNY = 0.137 USD
    'KRW': {'usd': 0.00071, 'rub': 0.065}, # 1 KRW = 0.00071 USD
    'USD': {'usd': 1.0, 'rub': 91.0},
}

def convert_to_usd(amount: float, currency: str) -> float:
    """Конвертация в USD"""
    rate = CURRENCY_RATES.get(currency, {}).get('usd', 0)
    return amount * rate

def convert_to_rub(amount: float, currency: str) -> float:
    """Конвертация в RUB"""
    # Через USD для точности
    usd_amount = convert_to_usd(amount, currency)
    rub_rate = CURRENCY_RATES.get('USD', {}).get('rub', 90)
    return usd_amount * rub_rate

# Обновление курсов (вручную или скриптом с cbr.ru)
def update_rates():
    """Обновить курсы (скрипт раз в неделю)"""
    # Парсинг cbr.ru (бесплатно, без API)
    pass
```

**Итого:** $0 за API валют

---

## 📤 6. Выгрузка на сайт (упрощенная)

### Вариант A: JSON файлы (проще всего)

```python
# export/json_exporter.py

def export_new_listings():
    """Экспорт новых лотов в JSON"""
    new_listings = db.get_not_exported(limit=1000)

    data = {
        "exported_at": datetime.now().isoformat(),
        "count": len(new_listings),
        "listings": []
    }

    for listing in new_listings:
        data["listings"].append({
            "id": listing['id'],
            "title": generate_title_ru(listing),
            "make": listing['make_ru'],
            "model": listing['model_ru'],
            "year": listing['year'],
            "mileage": listing['mileage'],
            "price": listing['price_rub'],
            "currency": "RUB",
            "images": json.loads(listing['images_json']),
            "url": listing['url'],
            "source": listing['source_site'],
            # Характеристики из справочников
            "transmission": listing['transmission_ru'],
            "fuel_type": listing['fuel_type_ru'],
            "drive_type": listing['drive_type_ru'],
            "body_type": listing['body_type_ru'],
            "color": listing['color_ru'],
        })

    # Сохранение
    filename = f"export/listings_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Пометить как экспортированные
    db.mark_exported([l['id'] for l in new_listings])

    return filename
```

**Ваш сайт читает JSON файлы** и импортирует к себе.

### Вариант B: Прямой доступ к SQLite

Если сайт на том же ПК:
```python
# На сайте просто подключаемся к той же БД
import sqlite3

conn = sqlite3.connect('C:\\Data\\Autos\\autos.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT l.*, m.name_ru as make_ru, mo.name_ru as model_ru,
           t.name_ru as transmission_ru, f.name_ru as fuel_type_ru
    FROM listings l
    JOIN car_makes m ON l.make_id = m.id
    JOIN car_models mo ON l.model_id = mo.id
    JOIN ref_transmission t ON l.transmission_id = t.id
    JOIN ref_fuel_type f ON l.fuel_type_id = f.id
    WHERE l.status = 'active'
    ORDER BY l.created_at DESC
    LIMIT 100
""")
```

**Итого:** $0 за выгрузку

---

## 💰 7. Итоговая стоимость (версия 2.0)

### Единоразовые расходы

| Статья | Стоимость |
|--------|-----------|
| HDD 500GB (если нет) | $50-60 |
| Перевод словарей (DeepL 1 раз) | $1 |
| **Итого** | **~$60** |

### Ежемесячные расходы

| Статья | Стоимость | Примечание |
|--------|-----------|------------|
| **Прокси Residential** | $60-80 | 10GB (Smartproxy/IPRoyal) |
| **Прокси Mobile** | $40-50 | 2GB для Encar |
| **Электроэнергия** | $10-20 | Локальный ПК |
| **Обновление словарей** | $0 | После первого раза |
| **Итого** | **$110-150/мес** | |

### Сравнение с версией 1.0

| Показатель | Версия 1.0 | Версия 2.0 | Разница |
|------------|------------|------------|---------|
| Единоразово | $0 | $60 | +$60 |
| В месяц | $405-780 | $110-150 | **-$540** |
| В год | $4,860-9,360 | $1,320-1,800 | **-$6,500** |

---

## 🚀 8. План внедрения (Budget версия)

### Неделя 1: Подготовка

- [ ] Купить прокси (тестовые 5GB)
- [ ] Создать структуру папок
- [ ] Настроить словари (zh_ru.json, ko_ru.json)
- [ ] Перевести справочники (DeepL, 1 раз)

### Неделя 2-3: Парсеры

- [ ] Базовый класс (aiohttp)
- [ ] che168 парсер (MVP)
- [ ] dongchedi парсер
- [ ] encar парсер (Playwright)

### Неделя 4: Интеграция

- [ ] SQLite подключение
- [ ] Генерация заголовков
- [ ] Конвертер валют
- [ ] JSON экспорт

### Неделя 5: Тестирование

- [ ] Запуск полного цикла
- [ ] Проверка анти-детекта
- [ ] Настройка расписания

---

## ⚠️ 9. Риски и решения (Budget)

| Риск | Вероятность | Решение |
|------|------------|---------|
| Блокировка IP | Высокая | Прокси ротация |
| Изменение структуры | Средняя | Мониторинг, алерты |
| CAPTCHA на Encar | Средняя | Mobile proxy + 2Captcha |
| Мало трафика прокси | Средняя | Увеличить лимит |
| **Перевод описаний** | **Низкая** | **Не переводить вообще** |

---

## 📝 10. Рекомендации

### Критически важно

1. **Словари** — перевести 1 раз, использовать всегда
2. **Прокси** — не экономить, это основа
3. **Бэкапы БД** — раз в день на отдельный диск
4. **Мониторинг** — хотя бы логи в файл

### Можно добавить потом

- [ ] Перевод описаний для VIP-лотов (DeepL)
- [ ] Кэширование изображений локально
- [ ] Telegram уведомления об ошибках
- [ ] Веб-интерфейс для управления

### Следующие шаги

1. ✅ Архитектура утверждена
2. ⏳ Создать `.env` и `requirements.txt`
3. ⏳ Заказать прокси (Smartproxy 5GB тест)
4. ⏳ Создать словари терминов
5. ⏳ Начать с che168 парсера

---

## 📎 Приложение: Готовые словари

### Китайский → Русский (полный список для перевода)

```
Трансмиссия:
自动挡 → АКПП
手动挡 → МКПП
手自一体 → Робот (AMT)
无级变速 → Вариатор (CVT)

Топливо:
汽油 → Бензин
柴油 → Дизель
纯电动 → Электро
混合动力 → Гибрид
插电混动 → Плагин-гибрид

Привод:
前置前驱 → Передний
前置后驱 → Задний
前置四驱 → Полный
四驱 → 4WD

Кузов:
轿车 → Седан
SUV → Внедорожник
MPV → Минивэн
跑车 → Купе
敞篷 → Кабриолет
旅行车 → Универсал
两厢 → Хэтчбек

Цвета:
白色 → Белый
黑色 → Черный
灰色 → Серый
银色 → Серебристый
红色 → Красный
蓝色 → Синий
棕色 → Коричневый
金色 → Золотой
```

### Корейский → Русский

```
Трансмиссия:
자동변속기 → АКПП
수동변속기 → МКПП
자동수동 → Робот
무단변속기 → Вариатор

Топливо:
가솔린 → Бензин
디젤 → Дизель
전기 → Электро
하이브리드 → Гибрид
플러그인하이브리드 → Плагин-гибрид

Привод:
전륜구동 → Передний
후륜구동 → Задний
사륜구동 → Полный
4 륜구동 → 4WD

Кузов:
세단 → Седан
SUV → Внедорожник
미니밴 → Минивэн
쿠페 → Купе
컨버터블 → Кабриолет
왜건 → Универсал
해치백 → Хэтчбек

Цвета:
흰색 → Белый
검은색 → Черный
회색 → Серый
은색 → Серебристый
빨간색 → Красный
파란색 → Синий
갈색 → Коричневый
```

---

**Версия:** 2.0 Budget
**Дата:** 2025-03-25
**Экономия:** ~$6,500/год
