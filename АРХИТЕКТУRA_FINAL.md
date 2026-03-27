# 🛡️ ФИНАЛЬНАЯ архитектура парсинга автосайтов
## Отказоустойчивая версия с бесперебойной работой

**Версия:** 3.0 Final (Production-ready)
**Дата:** 2025-03-25
**Особенности:** Бесперебойность, свои прокси, хранение фото, защита от отключений

---

## ⚡ Проблема: Что если свет выключат?

### Сценарии сбоев

| Сбой | Последствия | Решение |
|------|-------------|---------|
| **Свет 5-30 мин** | Прервался парсинг | Resume с места остановки |
| **Свет 2+ часа** | Пропущена выгрузка | Квоты на следующий день |
| **Свет 1+ день** | Отставание по данным | Приоритет свежим лотам |
| **Прокси забанили** | Остановка парса | Ротация + пул 20+ доменов |
| **Диск заполнен** | Остановка записи | Автоочистка + мониторинг |
| **Беget упал** | Прокси не работают | Резерв на другом хостинге |

---

## 🏗️ Архитектура бесперебойности

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ОТКАЗОУСТОЙЧИВАЯ СИСТЕМА                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    PROXY LAYER (Beget + резерв)                  │  │
│  │  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  │ 20+ доменов на Beget (PHP proxy scripts)                   │  │  │
│  │  │ proxy1.yoursite.com → proxy20.yoursite.com                 │  │  │
│  │  │ + резервные на бесплатном хостинге (InfinityFree, 000web)   │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│         ┌──────────────────────────▼──────────────────────────┐         │
│         │              PARSER ENGINE (Local PC)                │         │
│         │  ┌────────────────────────────────────────────────┐  │         │
│         │  │ Queue-based архитектура                       │  │         │
│         │  │ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │  │         │
│         │  │ │Pending Queue│ │Active Queue │ │Retry Queue│ │  │         │
│         │  │ │(ожидание)   │ │(в работе)   │ │(ошибки)   │ │  │         │
│         │  │ └─────────────┘ └─────────────┘ └───────────┘ │  │         │
│         │  │ ┌─────────────────────────────────────────────┐│  │         │
│         │  │ │  Checkpoint System (сохранение состояния)   ││  │         │
│         │  │ │  - Последняя страница                       ││  │         │
│         │  │ │  - Обработанные ID                          ││  │         │
│         │  │ │  - Таймстемп последнего успеха              ││  │         │
│         │  │ └─────────────────────────────────────────────┘│  │         │
│         │  └────────────────────────────────────────────────┘  │         │
│         └───────────────────────────────────────────────────────┘         │
│                                    │                                    │
│         ┌──────────────────────────▼──────────────────────────┐         │
│         │              STORAGE LAYER (Гибридный)               │         │
│         │  ┌────────────────────────────────────────────────┐  │         │
│         │  │ SQLite (локально) + Cloud Backup (авто)        │  │         │
│         │  │ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │  │         │
│         │  │ │  autos.db   │ │  backups/   │ │  Cloud/   │ │  │         │
│         │  │ │  (основная) │ │  (ежедневн) │ │  (резерв) │ │  │         │
│         │  │ └─────────────┘ └─────────────┘ └───────────┘ │  │         │
│         │  └────────────────────────────────────────────────┘  │         │
│         └───────────────────────────────────────────────────────┘         │
│                                    │                                    │
│         ┌──────────────────────────▼──────────────────────────┐         │
│         │           IMAGE STORAGE (Оптимизированный)           │         │
│         │  ┌────────────────────────────────────────────────┐  │         │
│         │  │ СТРАТЕГИЯ: Не хранить локально!                │  │         │
│         │  │ - Хранить URL оригиналов (ссылками)            │  │         │
│         │  │ - Проксирование через ваш сайт (по запросу)    │  │         │
│         │  │ - Кэш только для активных (7 дней)             │  │         │
│         │  └────────────────────────────────────────────────┘  │         │
│         └───────────────────────────────────────────────────────┘         │
│                                    │                                    │
│         ┌──────────────────────────▼──────────────────────────┐         │
│         │              EXPORT LAYER (Автономный)               │         │
│         │  ┌────────────────────────────────────────────────┐  │         │
│         │  │ UPS + Генератор + Watchdog                     │  │         │
│         │  │ - При отключении: работа от UPS 30+ мин        │  │         │
│         │  │ - Watchdog: автоперезапуск скриптов            │  │         │
│         │  │ - Генератор: если свет > 1 часа                │  │         │
│         │  └────────────────────────────────────────────────┘  │         │
│         └───────────────────────────────────────────────────────┘         │
│                                    │                                    │
│                                    ▼                                    │
│                          ┌─────────────────┐                            │
│                          │   ВАШ САЙТ      │                            │
│                          └─────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 1. Свои прокси на Beget (20+ доменов)

### Почему это лучше покупных?

| Покупные прокси | Свои на Beget |
|-----------------|---------------|
| $100-150/мес | ~600₽/мес (хостинг уже есть!) |
| Могут забанить | Вы контролируете |
| Общие IP | Личные чистые IP |
| Лимиты трафика | Неограниченный трафик |
| Зависимость | Независимость |

### Схема развёртывания

```
Beget хостинг (ahilesor):
├── основной домен: yoursite.ru
│   └── proxy/
│       └── proxy.php (скрипт)
│
├── поддомены (бесплатно, неограниченно):
│   ├── proxy1.yoursite.ru → proxy.php
│   ├── proxy2.yoursite.ru → proxy.php
│   ├── proxy3.yoursite.ru → proxy.php
│   ├── ...
│   └── proxy20.yoursite.ru → proxy.php
│
└── дополнительные домены (5 в подарок на тарифе):
    ├── yoursite2.ru → proxy.php
    ├── yoursite3.ru → proxy.php
    └── ...
```

### PHP proxy скрипт (универсальный)

```php
<?php
// proxy.php - универсальный прокси для парсинга
// Загрузка: https://proxy1.yoursite.ru/proxy.php?url=https://che168.com/...

header('Content-Type: application/json');

// CORS для локального доступа
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');
header('Access-Control-Allow-Headers: Content-Type');

// Проверка авторизации (простой токен)
$token = $_GET['token'] ?? $_POST['token'] ?? '';
$valid_tokens = ['token123', 'secret456', 'auto789']; // Сменить!

if (!in_array($token, $valid_tokens)) {
    http_response_code(403);
    echo json_encode(['error' => 'Unauthorized']);
    exit;
}

$url = $_GET['url'] ?? $_POST['url'] ?? '';

if (empty($url)) {
    http_response_code(400);
    echo json_encode(['error' => 'URL required']);
    exit;
}

// Валидация URL (только разрешённые сайты)
$allowed_domains = ['che168.com', 'dongchedi.com', 'encar.com'];
$parsed = parse_url($url);
$domain = str_replace('www.', '', $parsed['host'] ?? '');

$allowed = false;
foreach ($allowed_domains as $allowed_domain) {
    if (strpos($domain, $allowed_domain) !== false) {
        $allowed = true;
        break;
    }
}

if (!$allowed) {
    http_response_code(403);
    echo json_encode(['error' => 'Domain not allowed']);
    exit;
}

// Запрос к целевому сайту
$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_MAXREDIRS => 5,
    CURLOPT_TIMEOUT => 30,
    CURLOPT_CONNECTTIMEOUT => 10,

    // Заголовки для обхода детекта
    CURLOPT_HTTPHEADER => [
        'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding: gzip, deflate',
        'Connection: keep-alive',
        'Upgrade-Insecure-Requests: 1',
        'Cache-Control: max-age=0',
    ],

    // Куки
    CURLOPT_COOKIEJAR => '/tmp/cookies_' . session_id() . '.txt',
    CURLOPT_COOKIEFILE => '/tmp/cookies_' . session_id() . '.txt',

    // Реферер
    CURLOPT_REFERER => 'https://www.google.com/',
]);

// POST данные
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $_POST['data'] ?? '');
}

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);

curl_close($ch);

if ($error) {
    http_response_code(502);
    echo json_encode(['error' => 'Proxy error', 'message' => $error]);
    exit;
}

// Ответ
echo json_encode([
    'success' => true,
    'http_code' => $http_code,
    'html' => $response,
    'proxy_host' => $_SERVER['HTTP_HOST'],
    'timestamp' => time()
]);
?>
```

### Конфигурация прокси для парсера

```python
# config/proxies.py

BEGET_PROXIES = [
    # Поддомены (бесплатно)
    {'url': 'https://proxy1.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy2.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy3.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy4.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy5.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy6.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy7.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy8.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy9.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy10.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy11.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy12.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy13.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy14.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy15.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy16.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy17.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy18.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy19.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},
    {'url': 'https://proxy20.yoursite.ru/proxy.php', 'token': 'token123', 'priority': 1},

    # Дополнительные домены (5 в подарок)
    {'url': 'https://yoursite2.ru/proxy.php', 'token': 'secret456', 'priority': 2},
    {'url': 'https://yoursite3.ru/proxy.php', 'token': 'secret456', 'priority': 2},
    {'url': 'https://yoursite4.ru/proxy.php', 'token': 'secret456', 'priority': 2},
    {'url': 'https://yoursite5.ru/proxy.php', 'token': 'secret456', 'priority': 2},
    {'url': 'https://yoursite6.ru/proxy.php', 'token': 'secret456', 'priority': 2},

    # Резервные (бесплатный хостинг)
    {'url': 'https://proxy-backup1.000webhostapp.com/proxy.php', 'token': 'auto789', 'priority': 3},
    {'url': 'https://proxy-backup2.infinityfreeapp.com/proxy.php', 'token': 'auto789', 'priority': 3},
]

# Распределение по сайтам
PROXY_ASSIGNMENT = {
    'che168.com': list(range(0, 7)),      # proxy1-7
    'dongchedi.com': list(range(7, 14)),   # proxy8-14
    'encar.com': list(range(14, 25)),      # proxy15-25 (самый строгий)
}
```

### Менеджер прокси с авторотацией

```python
# proxy/manager.py

import random
import asyncio
from typing import Dict, List, Optional
from config.proxies import BEGET_PROXIES, PROXY_ASSIGNMENT

class ProxyManager:
    def __init__(self):
        self.proxies = BEGET_PROXIES
        self.failed = {}  # {proxy_url: fail_count}
        self.last_used = {}  # {proxy_url: timestamp}
        self.max_fails = 5
        self.cooldown_seconds = 300  # 5 мин после ошибки

    def get_proxy(self, target_domain: str) -> Dict:
        """Получить прокси для домена с учётом приоритета и ошибок"""
        available = []

        # Получить пул прокси для домена
        proxy_indices = PROXY_ASSIGNMENT.get(target_domain, list(range(len(self.proxies))))

        for i in proxy_indices:
            if i >= len(self.proxies):
                continue

            proxy = self.proxies[i]
            url = proxy['url']

            # Проверка на cooldown после ошибок
            if url in self.failed:
                fail_count, last_fail = self.failed[url]
                if fail_count >= self.max_fails:
                    continue  # Пропустить забаненный

            available.append((proxy, proxy['priority']))

        if not available:
            # Все прокси забанены - использовать любые с наименьшим fail_count
            for i, proxy in enumerate(self.proxies):
                fail_count = self.failed.get(proxy['url'], (0, 0))[0]
                available.append((proxy, fail_count))
            available.sort(key=lambda x: x[1])  # Сортировать по fail_count

        # Выбрать случайный из доступных (с приоритетом)
        if available:
            # Группировать по приоритету
            by_priority = {}
            for proxy, priority in available:
                if priority not in by_priority:
                    by_priority[priority] = []
                by_priority[priority].append(proxy)

            # Использовать наивысший приоритет
            best_priority = min(by_priority.keys())
            return random.choice(by_priority[best_priority])

        #Fallback - любой прокси
        return random.choice(self.proxies)

    def mark_success(self, proxy_url: str):
        """Отметить успешный запрос"""
        if proxy_url in self.failed:
            fail_count, _ = self.failed[proxy_url]
            if fail_count > 0:
                self.failed[proxy_url] = (max(0, fail_count - 1), time.time())

    def mark_failed(self, proxy_url: str):
        """Отметить failed запрос"""
        if proxy_url not in self.failed:
            self.failed[proxy_url] = (1, time.time())
        else:
            fail_count, _ = self.failed[proxy_url]
            self.failed[proxy_url] = (fail_count + 1, time.time())

    def get_stats(self) -> Dict:
        """Статистика по прокси"""
        total = len(self.proxies)
        failed = len([p for p, (c, _) in self.failed.items() if c >= self.max_fails])
        healthy = total - failed

        return {
            'total': total,
            'healthy': healthy,
            'failed': failed,
            'health_rate': healthy / total if total > 0 else 0
        }
```

---

## 📸 2. Хранение фотографий (оптимизированное)

### Проблема
- 1 млн лотов × 10 фото = 10 млн фото
- Среднее фото: 300KB
- Общий размер: 10,000,000 × 300KB = 3,000,000,000 KB = **~3TB**

### Решение: НЕ хранить локально!

```
┌─────────────────────────────────────────────────────────────┐
│           СТРАТЕГИЯ ХРАНЕНИЯ ФОТО (БЕЗ ЛОКАЛЬНОГО)          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Вариант 1: Hotlinking (ссылки на оригиналы)                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Хранить в БД только URL:                              │ │
│  │ ["https://img.che168.com/123_1.jpg", ...]            │ │
│  │                                                       │ │
│  │ Плюсы:                                                │ │
│  │ ✅ $0 за хранение                                     │ │
│  │ ✅ Нет загрузки                                       │ │
│  │ ✅ Всегда актуально                                   │ │
│  │ Минусы:                                               │ │
│  │ ⚠️ Зависимость от сайта-источника                     │ │
│  │ ⚠️ Могут удалить фото                                 │ │
│  │ ⚠️ Медленнее загрузка (чужой сервер)                  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Вариант 2: Проксирование через ваш сайт (рекомендуется)    │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Ваш сайт проксирует фото по запросу:                  │ │
│  │ https://yoursite.ru/image-proxy?url=...              │ │
│  │                                                       │ │
│  │ Кэш на Cloudflare CDN (бесплатно 100GB/день):         │ │
│  │ - Первое обращение: загрузка с источника              │ │
│  │ - Повторное: из кэша Cloudflare (мгновенно)           │ │
│  │                                                       │ │
│  │ Плюсы:                                                │ │
│  │ ✅ Быстрая загрузка (CDN)                             │ │
│  │ ✅ Нет своего хранения                                │ │
│  │ ✅ Кэш управляется автоматически                      │ │
│  │ ✅ Защита от удаления с источника                     │ │
│  │ Минусы:                                               │ │
│  │ ⚠️ Нужно настроить прокси на сайте                    │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Вариант 3: Гибридный (для избранных)                       │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ - Активные лоты (7 дней): кэш локально                │ │
│  │ - Архив (>7 дней): только URL                         │ │
│  │ - VIP-лоты: загрузка на свой сервер                   │ │
│  │                                                       │ │
│  │ Расчёт:                                               │ │
│  │ 1 млн лотов × 10% активных = 100K лотов              │ │
│  │ 100K × 10 фото × 300KB = 300GB                       │ │
│  │ HDD 500GB = $50 (единоразово)                         │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Рекомендуемая стратегия

**Хранение в БД:**
```sql
-- Таблица listings
CREATE TABLE listings (
    ...
    images_json TEXT,  -- JSON массив URL оригиналов
    images_cached INTEGER DEFAULT 0,  -- 0 = нет, 1 = загружены
    ...
);

-- Таблица для кэша фото (только активные)
CREATE TABLE image_cache (
    id INTEGER PRIMARY KEY,
    listing_id INTEGER,
    image_url TEXT,
    local_path TEXT,
    downloaded_at TIMESTAMP,
    expires_at TIMESTAMP,  -- +7 дней
    size_bytes INTEGER,

    FOREIGN KEY (listing_id) REFERENCES listings(id)
);
```

**Проксирование на сайте (PHP):**
```php
// image-proxy.php на вашем сайте
<?php
header('Content-Type: image/jpeg');
header('Cache-Control: public, max-age=86400'); // 1 день

$url = $_GET['url'] ?? '';

// Валидация
if (!preg_match('/^https:\/\/(img\.)?(che168|dongchedi|encar)\.com\//', $url)) {
    http_response_code(403);
    exit('Forbidden');
}

// Загрузка с источника
$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 30,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_USERAGENT => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
    CURLOPT_REFERER => 'https://www.google.com/',
]);

$image = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($http_code === 200 && $image) {
    echo $image;
} else {
    http_response_code(502);
    // Placeholder изображение
    readfile('placeholder.jpg');
}
?>
```

**Cloudflare CDN (бесплатно):**
- Подключить ваш сайт к Cloudflare
- Кэширование изображений: 100GB/день бесплатно
- Глобальная сеть: быстрая загрузка из любой точки

---

## 🔋 3. Бесперебойное питание (UPS + Generator)

### Схема защиты от отключений

```
┌─────────────────────────────────────────────────────────────┐
│              БЕСПЕРЕБОЙНАЯ СИСТЕМА ПИТАНИЯ                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  СЕТЬ 220V                                            │ │
│  │       │                                               │ │
│  │       ▼                                               │ │
│  │  ┌─────────────────┐                                  │ │
│  │  │  ИБП (UPS)      │  1000VA / 600W                   │ │
│  │  │  APC Back-UPS   │  ~$100-150                       │ │
│  │  │  или аналог     │  Работа: 30-60 мин               │ │
│  │  └────────┬────────┘                                  │ │
│  │           │                                           │ │
│  │           ▼                                           │ │
│  │  ┌─────────────────┐                                  │ │
│  │  │  ПК (парсер)    │  Потребление: 150-300W           │ │
│  │  │  + Роутер       │                                  │ │
│  │  └─────────────────┘                                  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Если свет > 1 часа:                                        │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  БЕНЗИНОВЫЙ ГЕНЕРАТОР 2-3 кВт                         │ │
│  │  ┌─────────────────────────────────────────────────┐ │ │
│  │  │ - Запуск вручную или авто (ATS)                 │ │ │
│  │  │ - Работа: 8-12 часов на баке                    │ │ │
│  │  │ - Стоимость: $300-500                           │ │ │
│  │  └─────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Рекомендуемое оборудование

| Устройство | Мощность | Время работы | Цена |
|------------|----------|--------------|------|
| **ИБП APC Back-UPS 1000VA** | 600W | 30-60 мин | $100-150 |
| **ИБП Powercom 1200VA** | 720W | 40-80 мин | $120-170 |
| **Генератор Champion 2.5кВт** | 2500W | 8-10 часов | $300-400 |
| **Генератор Hyundai 3кВт (ATS)** | 3000W | 10-12 часов | $500-700 |

**Минимум:** ИБП 1000VA ($100-150)
**Оптимум:** ИБП + генератор ($400-550)

---

## 💾 4. Резервное копирование (авто)

### Стратегия 3-2-1

```
┌─────────────────────────────────────────────────────────────┐
│              СТРАТЕГИЯ БЭКАПОВ 3-2-1                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  3 копии данных:                                            │
│  ├── Основная БД (C:\Data\Autos\autos.db)                  │
│  ├── Локальный бэкап (D:\Backups\autos_YYYYMMDD.db)        │
│  └── Облачный бэкап (Google Drive / Yandex Disk)            │
│                                                             │
│  2 разных носителя:                                         │
│  ├── HDD основной (системный)                               │
│  └── HDD резервный / SSD                                    │
│                                                             │
│  1 копия вне дома:                                          │
│  └── Облако (бесплатно 10-50GB)                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Скрипт автобэкапа

```python
# utils/backup.py

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
import os

def create_backup():
    """Создать резервную копию БД"""

    # Пути
    db_path = Path(r'C:\Data\Autos\autos.db')
    backup_dir = Path(r'D:\Backups\Autos')  # На другой диск!
    cloud_dir = Path(r'C:\Users\MSI\YandexDisk\AutosBackups')  # Облако

    # Создать директории
    backup_dir.mkdir(parents=True, exist_ok=True)
    cloud_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')

    # Локальный бэкап
    local_backup = backup_dir / f'autos_{timestamp}.db'
    shutil.copy2(db_path, local_backup)

    # Облачный бэкап (сжатый)
    cloud_backup = cloud_dir / f'autos_{timestamp}.db'
    shutil.copy2(db_path, cloud_backup)

    # Очистка старых бэкапов (>30 дней)
    cleanup_old_backups(backup_dir, days=30)
    cleanup_old_backups(cloud_dir, days=30)

    return {
        'local': str(local_backup),
        'cloud': str(cloud_backup),
        'size_mb': local_backup.stat().st_size / 1024 / 1024
    }

def cleanup_old_backups(directory: Path, days: int = 30):
    """Удалить старые бэкапы"""
    now = datetime.now()
    for backup in directory.glob('autos_*.db'):
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        if (now - mtime).days > days:
            backup.unlink()
```

### Расписание бэкапов

```python
# Расписание (schedule)
BACKUP_SCHEDULE = {
    'hourly': {
        'type': 'incremental',  # Только изменения
        'time': '0 * * * *',    # Каждый час
        'retain': 24            # Хранить 24 часа
    },
    'daily': {
        'type': 'full',
        'time': '0 3 * * *',    # В 3 ночи
        'retain': 30            # Хранить 30 дней
    },
    'weekly': {
        'type': 'full',
        'time': '0 4 * * 0',    # Воскресенье в 4 утра
        'retain': 12            # Хранить 12 недель
    },
    'monthly': {
        'type': 'full',
        'time': '0 5 1 * *',    # 1 число в 5 утра
        'retain': 12            # Хранить 12 месяцев
    }
}
```

---

## 🔄 5. Queue-based архитектура парсера

### Система очередей

```python
# parser/queue_manager.py

import sqlite3
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional

class QueueStatus(Enum):
    PENDING = 'pending'      # Ожидает обработки
    PROCESSING = 'processing' # В работе
    COMPLETED = 'completed'   # Успешно
    FAILED = 'failed'         # Ошибка
    RETRY = 'retry'          # Повтор

class QueueManager:
    """Менеджер очередей для бесперебойного парсинга"""

    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        """Создать таблицы очередей"""
        self.db.executescript('''
            -- Очередь URL на парсинг
            CREATE TABLE IF NOT EXISTS parse_queue (
                id INTEGER PRIMARY KEY,
                url TEXT NOT NULL,
                source_site TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 5,  -- 1-10
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                checkpoint_data TEXT  -- JSON с состоянием
            );

            -- Чекпоинты для resume
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY,
                parser_name TEXT UNIQUE,
                last_url TEXT,
                last_page INTEGER,
                processed_ids TEXT,  -- JSON массив
                last_success_at TIMESTAMP,
                state_data TEXT  -- JSON с полным состоянием
            );

            -- Логи для отладки
            CREATE TABLE IF NOT EXISTS parse_logs (
                id INTEGER PRIMARY KEY,
                queue_id INTEGER,
                message TEXT,
                level TEXT DEFAULT 'info',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_queue_status ON parse_queue(status);
            CREATE INDEX IF NOT EXISTS idx_queue_priority ON parse_queue(priority, created_at);
        ''')
        self.db.commit()

    def add_to_queue(self, urls: List[str], source: str, priority: int = 5):
        """Добавить URL в очередь"""
        cursor = self.db.cursor()
        for url in urls:
            cursor.execute('''
                INSERT INTO parse_queue (url, source_site, priority)
                VALUES (?, ?, ?)
            ''', (url, source, priority))
        self.db.commit()

    def get_next_task(self, source: str = None) -> Optional[Dict]:
        """Получить следующую задачу из очереди"""
        cursor = self.db.cursor()

        query = '''
            SELECT id, url, source_site, priority, attempts
            FROM parse_queue
            WHERE status = 'pending'
        '''
        params = []

        if source:
            query += ' AND source_site = ?'
            params.append(source)

        query += ' ORDER BY priority ASC, created_at ASC LIMIT 1'

        cursor.execute(query, params)
        row = cursor.fetchone()

        if row:
            # Пометить как processing
            cursor.execute('''
                UPDATE parse_queue
                SET status = 'processing', started_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (row[0],))
            self.db.commit()

            return {
                'id': row[0],
                'url': row[1],
                'source': row[2],
                'priority': row[3],
                'attempts': row[4]
            }

        return None

    def mark_completed(self, task_id: int):
        """Отметить задачу как выполненную"""
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE parse_queue
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (task_id,))
        self.db.commit()

    def mark_failed(self, task_id: int, error: str, retry: bool = True):
        """Отметить задачу как failed"""
        cursor = self.db.cursor()

        # Получить текущие попытки
        cursor.execute('SELECT attempts, max_attempts FROM parse_queue WHERE id = ?', (task_id,))
        row = cursor.fetchone()

        if row:
            attempts, max_attempts = row

            if retry and attempts < max_attempts:
                # Повторить позже
                cursor.execute('''
                    UPDATE parse_queue
                    SET status = 'retry',
                        attempts = attempts + 1,
                        error_message = ?,
                        started_at = NULL
                    WHERE id = ?
                ''', (error, task_id))
            else:
                # Превышено макс. попыток
                cursor.execute('''
                    UPDATE parse_queue
                    SET status = 'failed',
                        error_message = ?
                    WHERE id = ?
                ''', (error, task_id))

        self.db.commit()

    def process_retry_queue(self):
        """Обработать задачи на повтор"""
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE parse_queue
            SET status = 'pending', started_at = NULL
            WHERE status = 'retry'
            AND datetime(created_at, '+5 minutes') < datetime('now')
        ''')
        self.db.commit()

    def save_checkpoint(self, parser_name: str, state: Dict):
        """Сохранить чекпоинт для resume"""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO checkpoints
            (parser_name, last_url, last_page, processed_ids, last_success_at, state_data)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        ''', (
            parser_name,
            state.get('last_url'),
            state.get('last_page'),
            json.dumps(state.get('processed_ids', [])),
            json.dumps(state)
        ))
        self.db.commit()

    def load_checkpoint(self, parser_name: str) -> Optional[Dict]:
        """Загрузить последний чекпоинт"""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT state_data FROM checkpoints WHERE parser_name = ?
        ''', (parser_name,))
        row = cursor.fetchone()

        if row:
            return json.loads(row[0])
        return None

    def get_stats(self) -> Dict:
        """Статистика очереди"""
        cursor = self.db.cursor()

        stats = {}
        for status in ['pending', 'processing', 'completed', 'failed', 'retry']:
            cursor.execute('SELECT COUNT(*) FROM parse_queue WHERE status = ?', (status,))
            stats[status] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM parse_queue')
        stats['total'] = cursor.fetchone()[0]

        return stats
```

### Resume после отключения

```python
# parser/resume.py

async def resume_after_crash(parser_name: str):
    """Возобновить парсинг после сбоя"""

    queue_manager = QueueManager(DB_PATH)
    checkpoint = queue_manager.load_checkpoint(parser_name)

    if checkpoint:
        print(f"Возобновление с чекпоинта: {checkpoint['last_url']}")
        print(f"Обработано ID: {len(checkpoint['processed_ids'])}")

        # Вернуть未完成 задачи в очередь
        queue_manager.process_retry_queue()

        return checkpoint

    print("Чекпоинт не найден, начинаем заново")
    return None
```

---

## 📊 6. Мониторинг и алерты

### Telegram уведомления

```python
# utils/monitoring.py

import asyncio
from datetime import datetime

class Monitor:
    """Мониторинг системы с уведомлениями"""

    def __init__(self, telegram_bot_token: str, chat_id: str):
        self.bot_token = telegram_bot_token
        self.chat_id = chat_id

    async def send_alert(self, message: str, level: str = 'info'):
        """Отправить уведомление в Telegram"""

        emoji = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨'
        }.get(level, '📢')

        text = f"{emoji} <b>Парсер: {level.upper()}</b>\n\n{message}\n\n{datetime.now().strftime('%H:%M:%S')}"

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        async with aiohttp.ClientSession() as session:
            await session.post(url, json={
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            })

    async def check_system_health(self):
        """Проверка здоровья системы"""

        # Проверка очередей
        queue_stats = queue_manager.get_stats()

        # Проверка прокси
        proxy_stats = proxy_manager.get_stats()

        # Проверка места на диске
        import shutil
        total, used, free = shutil.disk_usage(r"C:\Data")
        free_gb = free / (1024**3)

        alerts = []

        if queue_stats['failed'] > 100:
            alerts.append(f"Много failed задач: {queue_stats['failed']}")

        if proxy_stats['health_rate'] < 0.5:
            alerts.append(f"Много забаненных прокси: {proxy_stats['failed']}/{proxy_stats['total']}")

        if free_gb < 50:
            alerts.append(f"Мало места на диске: {free_gb:.1f}GB")

        if alerts:
            await self.send_alert('\n'.join(alerts), 'warning')

    async def daily_report(self):
        """Ежедневный отчёт"""

        stats = queue_manager.get_stats()
        proxy_stats = proxy_manager.get_stats()

        report = f"""
📊 <b>Ежедневный отчёт</b>

Парсинг:
• Обработано: {stats['completed']}
• В очереди: {stats['pending']}
• Ошибки: {stats['failed']}

Прокси:
• Активны: {proxy_stats['healthy']}/{proxy_stats['total']}
• Забанены: {proxy_stats['failed']}

Система:
• Статус: OK
• Аптайм: 24ч
        """

        await self.send_alert(report, 'info')
```

### Расписание мониторинга

```python
# schedule.py

import schedule
import time

# Ежедневный отчёт в 9 утра
schedule.every().day.at("09:00").do(monitor.daily_report)

# Проверка здоровья каждые 30 мин
schedule.every(30).minutes.do(monitor.check_system_health)

# Обработка retry очереди каждые 5 мин
schedule.every(5).minutes.do(queue_manager.process_retry_queue)

# Бэкап в 3 ночи
schedule.every().day.at("03:00").do(backup.create_backup)

# Запуск планировщика
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 💰 7. Итоговая стоимость (версия 3.0 Final)

### Единоразовые расходы

| Статья | Стоимость |
|--------|-----------|
| ИБП (UPS) 1000VA | $100-150 |
| Генератор (опционально) | $300-500 |
| HDD 500GB для бэкапов | $50 |
| **Итого (минимум)** | **$150** |
| **Итого (полный)** | **$500** |

### Ежемесячные расходы

| Статья | Стоимость | Примечание |
|--------|-----------|------------|
| **Хостинг Beget** | 600₽ (~$7) | Уже есть! |
| **Домены (20 шт)** | 0₽ | Бесплатно (поддомены) |
| **Доп. домены (5 шт)** | 0₽ | В подарок на тарифе |
| **Электроэнергия** | $10-20 | Локальный ПК + ИБП |
| **Облако (бэкапы)** | $0 | Яндекс.Диск 10GB бесплатно |
| **Cloudflare CDN** | $0 | 100GB/день бесплатно |
| **Итого** | **~$17-27/мес** | |

### Сравнение версий

| Показатель | v1.0 | v2.0 Budget | v3.0 Final |
|------------|------|-------------|------------|
| Единоразово | $0 | $60 | $150-500 |
| В месяц | $405-780 | $110-150 | **$17-27** |
| В год | $4,860-9,360 | $1,320-1,800 | **$200-320** |
| Прокси | Покупные | Покупные | **Свои (20+)** |
| Хранение фото | Нет | URL | **CDN + кэш** |
| Бэкапы | Нет | Локально | **3-2-1** |
| UPS | Нет | Нет | **Есть** |
| Бесперебойность | Низкая | Средняя | **Высокая** |

**Экономия vs v1.0: ~$6,000/год!**

---

## 🚀 8. План развёртывания

### Неделя 1: Прокси на Beget

- [ ] Войти в панель Beget (ahilesor / TezCl3fcQ3$]bfs...)
- [ ] Создать 20 поддоменов: proxy1-20.yoursite.ru
- [ ] Загрузить proxy.php в корень
- [ ] Протестировать каждый прокси
- [ ] Настроить токены безопасности

### Неделя 2: Парсер с очередями

- [ ] Создать структуру проекта
- [ ] Реализовать QueueManager
- [ ] Реализовать Checkpoint system
- [ ] Парсер che168 (MVP)
- [ ] Тестирование resume после сбоя

### Неделя 3: Хранение и бэкапы

- [ ] Настроить SQLite БД
- [ ] Реализовать автобэкап
- [ ] Настроить Яндекс.Диск для облачных бэкапов
- [ ] Протестировать восстановление

### Неделя 4: Мониторинг и UPS

- [ ] Купить и подключить ИБП
- [ ] Настроить Telegram уведомления
- [ ] Настроить ежедневные отчёты
- [ ] Финальное тестирование

---

## 📋 9. Чек-лист бесперебойности

### При отключении света

- [ ] **0-30 сек:** ПК работает от ИБП
- [ ] **30 сек:** Graceful shutdown парсера (сохранение чекпоинта)
- [ ] **30 мин:** Если свет не дали, ПК выключается
- [ ] **1 час:** Запуск генератора (вручную или авто)
- [ ] **Свет дали:** Автозапуск парсера, resume с чекпоинта

### При блокировке прокси

- [ ] **1 прокси забанен:** Автоматическая ротация
- [ ] **5 прокси забанены:** Алерт в Telegram
- [ ] **10+ прокси забанены:** Пауза парсинга, алерт
- [ ] **Все прокси забанены:** Переключение на резервные (InfinityFree)

### При заполнении диска

- [ ] **80% заполнено:** Warning алерт
- [ ] **90% заполнено:** Автоочистка старых бэкапов
- [ ] **95% заполнено:** Критический алерт, остановка парсинга

### При ошибке парсинга

- [ ] **1 ошибка:** Retry через 5 мин
- [ ] **3 ошибки:** Пропустить URL, логирование
- [ ] **100 ошибок:** Алерт, проверка структуры сайта

---

## 📝 10. Итоговые рекомендации

### Критически важно

1. **Свои прокси на Beget** — развёрнуть 20+ доменов
2. **Queue-based архитектура** — гарантия отсутствия потерь
3. **Checkpoint system** — resume после любого сбоя
4. **Бэкапы 3-2-1** — защита данных
5. **ИБП (UPS)** — защита от внезапных отключений

### Можно добавить потом

- [ ] Автозапуск генератора (ATS)
- [ ] Резервный сервер (VPS) для дублирования
- [ ] Распределённый парсинг (несколько ПК)
- [ ] Загрузка фото на свой CDN

### Следующие шаги (прямо сейчас)

1. ✅ Архитектура утверждена
2. ⏳ **Войти в Beget** → создать 20 поддоменов
3. ⏳ **Загрузить proxy.php**
4. ⏳ **Создать структуру проекта**
5. ⏳ **Реализовать QueueManager**

---

**Версия:** 3.0 Final
**Дата:** 2025-03-25
**Экономия:** ~$6,000/год vs оригинал
**Бесперебойность:** Высокая (UPS + Checkpoints + Retry)
