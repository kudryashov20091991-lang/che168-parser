"""
Парсер che168.com с прокси ротацией
Прокси: 45.32.56.105:1385X с авторизацией логин:пароль
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Прокси с авторизацией
PROXIES = [
    {"server": "45.32.56.105:13851", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "45.32.56.105:13852", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "45.32.56.105:13853", "username": "Ek0G8F", "password": "GR0Fhj"},
]

# Словарь авто-терминов китайско-русский
ZH_RU_DICT = {
    "万公里": " тыс. км",
    "万公里／": " тыс. км / ",
    "年": " г.",
    "北京": "Пекин",
    "上海": "Шанхай",
    "广州": "Гуанчжоу",
    "深圳": "Шэньчжэнь",
    "奔驰": "Mercedes-Benz",
    "宝马": "BMW",
    "奥迪": "Audi",
    "保时捷": "Porsche",
    "路虎": "Land Rover",
    "揽胜": "Range Rover",
    "奔驰 S 级": "Mercedes-Benz S-Class",
    "奔驰 S": "Mercedes-Benz S",
    "S 级": "S-Class",
    "奥迪 A6L": "Audi A6L",
    "Model Y": "Tesla Model Y",
    "款": "",
    "改款": "рестайлинг",
    "舒适版": "Comfort",
    "豪华型": "Luxury",
    "运动型": "Sport",
    "商务型": "Business",
    "四驱": "4WD",
    "自动": "АКПП",
    "手动": "МКПП",
    "万": "",
    "／": " / ",
    "传世加长版": "LWB",
    "后轮驱动版": "RWD",
    "长续航全轮驱动版": "Long Range AWD",
    "两驱": "2WD",
    "现代": "Hyundai",
    "天籁": "Nissan Teana",
    "轩逸": "Nissan Sylphy",
    "金杯海狮": "Jinbei Haishi",
    "Polo": "VW Polo",
    "第五代快运王": "5th Gen Express",
}

def translate_to_russian(text):
    result = text
    for zh, ru in ZH_RU_DICT.items():
        result = result.replace(zh, ru)
    return result

def parse_price_cny(text):
    matches = re.findall(r'(\d+\.?\d*)\s*万', text)
    if matches:
        return float(matches[-1]) * 10000
    return 0

def parse_mileage_km(text):
    match = re.search(r'(\d+\.?\d*)\s*万公里', text)
    if match:
        return float(match.group(1)) * 10000
    return 0

def parse_year(text):
    match = re.search(r'(\d{4})-\d{1,2}', text)
    if match:
        return int(match.group(1))
    return 0

async def parse_with_proxy(proxy_info, proxy_index, cars_collected):
    """Парсинг с одним прокси"""
    proxy_server = proxy_info["server"]
    print(f"\n[Прокси {proxy_index + 1}] {proxy_server}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            context = await browser.new_context(
                proxy={
                    "server": f"http://{proxy_server}",
                    "username": proxy_info["username"],
                    "password": proxy_info["password"],
                },
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            page = await context.new_page()

            print(f"  Загрузка страницы...")
            await page.goto("https://www.che168.com/beijing/", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)

            # Проверяем IP через внешний сервис
            try:
                await page.goto("https://api.ipify.org?format=json", timeout=10000)
                ip_data = await page.evaluate("() => fetch('https://api.ipify.org?format=json').then(r => r.json())")
                print(f"  IP адрес: {ip_data.get('ip', 'не определен')}")
            except:
                print(f"  Не удалось определить IP")

            # Возвращаемся на сайт
            await page.goto("https://www.che168.com/beijing/", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(2)

            # Собираем данные
            car_data = await page.evaluate("""
                () => {
                    const cars = [];
                    const selectors = [
                        '[class*="car"]',
                        '[class*="vehicle"]',
                        '.car-list li',
                        'a[href*="/dealer/"]'
                    ];

                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach((el, i) => {
                            if (i < 20) {
                                const text = el.innerText || '';
                                const link = el.querySelector('a')?.href || '';
                                const img = el.querySelector('img')?.src || '';

                                if (text.length > 30 && text.includes('万')) {
                                    cars.push({
                                        title: text.replace(/\s+/g, ' ').trim(),
                                        raw: text.replace(/\s+/g, ' ').trim(),
                                        url: link,
                                        image: img
                                    });
                                }
                            }
                        });
                        if (cars.length >= 15) break;
                    }
                    return cars.slice(0, 15);
                }
            """)

            await browser.close()

            # Обрабатываем автомобили
            for i, car in enumerate(car_data):
                if len(cars_collected) >= 15:
                    break

                title = car.get("raw", car.get("title", ""))
                if not title:
                    continue

                price_cny = parse_price_cny(title)
                mileage_km = parse_mileage_km(title)
                year = parse_year(title)
                title_ru = translate_to_russian(title)
                price_rub = price_cny * 13

                car_info = {
                    "id": len(cars_collected) + 1,
                    "proxy_used": proxy_server,
                    "title_original": title,
                    "title_ru": title_ru,
                    "price_cny": price_cny,
                    "price_rub": round(price_rub, 2),
                    "mileage_km": mileage_km,
                    "year": year,
                    "image": car.get("image", ""),
                    "url": car.get("url", ""),
                    "source": "che168.com",
                    "location": "Пекин, Китай",
                }

                cars_collected.append(car_info)

                title_preview = title_ru[:80].encode('cp1251', errors='replace').decode('cp1251')
                print(f"  [{len(cars_collected)}] {title_preview}...")
                print(f"      Цена: {price_cny:,.0f} CNY / {price_rub:,.0f} RUB")

            return len(car_data)

    except Exception as e:
        print(f"  ОШИБКА: {str(e)[:200]}")
        return 0

async def parse_cars_with_rotation():
    """Парсинг 15 автомобилей с ротацией прокси"""
    print("=" * 60)
    print("ПАРСИНГ CHE168.COM С ПРОКСИ РОТАЦИЕЙ")
    print("=" * 60)
    print(f"Прокси: {len(PROXIES)} шт")
    print(f"Цель: 15 автомобилей (по 5 запросов с каждого прокси)")
    print(f"Интервал: 1 минута между запросами")

    cars_collected = []
    total_requests = 0
    proxy_index = 0

    while len(cars_collected) < 15:
        # Берем следующий прокси (ротация по кругу)
        proxy_info = PROXIES[proxy_index % len(PROXIES)]

        print(f"\n{'='*40}")
        print(f"ЗАПРОС №{total_requests + 1}")

        result = await parse_with_proxy(proxy_info, proxy_index % len(PROXIES), cars_collected)
        total_requests += 1
        proxy_index += 1

        if len(cars_collected) >= 15:
            break

        # Ждем 1 минуту перед следующим запросом
        print(f"\nОжидание 60 секунд перед следующим запросом...")
        await asyncio.sleep(60)

    # Сохраняем результаты
    print("\n" + "=" * 60)
    print("СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
    print("=" * 60)

    output_file = Path(__file__).parent / "che168_cars_proxy_15.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source": "che168.com",
            "total_cars": len(cars_collected),
            "total_requests": total_requests,
            "proxies_used": [p["server"] for p in PROXIES],
            "cars": cars_collected
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[ИТОГ] Сохранено {len(cars_collected)} автомобилей")
    print(f"Всего запросов: {total_requests}")
    print(f"Файл: {output_file}")

    # Генерируем HTML для сайта
    html_content = generate_html(cars_collected)
    html_file = Path(__file__).parent / "che168_cars_proxy_15.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML для сайта: {html_file}")

    return cars_collected

def generate_html(cars):
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Автомобили из Китая - che168.com</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .car-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .car-card { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; background: white; }
        .car-image { width: 100%; height: 200px; object-fit: cover; }
        .car-info { padding: 15px; }
        .car-title { font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c3e50; }
        .car-price { color: #e74c3c; font-size: 18px; font-weight: bold; }
        .car-details { color: #666; font-size: 14px; margin-top: 10px; }
        .car-details div { margin: 5px 0; }
        .proxy-info { font-size: 12px; color: #999; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>🚗 Автомобили из Китая (che168.com)</h1>
    <p>Выгружено: """ + datetime.now().strftime("%d.%m.%Y %H:%M") + """</p>
    <p>Использована ротация прокси для обхода блокировок</p>

    <div class="car-grid">
"""

    for car in cars:
        html += f"""
        <div class="car-card">
            <img src="{car['image']}" alt="{car['title_ru']}" class="car-image" onerror="this.src='https://via.placeholder.com/400x200?text=No+Image'">
            <div class="car-info">
                <div class="car-title">{car['title_ru']}</div>
                <div class="car-price">{car['price_rub']:,.0f} ₽</div>
                <div class="car-details">
                    <div>📅 Год: {car['year']}</div>
                    <div>🛣️ Пробег: {car['mileage_km']:,.0f} км</div>
                    <div>💰 Цена в Китае: {car['price_cny']:,.0f} CNY</div>
                    <div>📍 Город: {car['location']}</div>
                </div>
                <div class="proxy-info">Прокси: {car.get('proxy_used', 'N/A')}</div>
            </div>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    asyncio.run(parse_cars_with_rotation())
