"""
Парсер che168.com - 10 автомобилей через ПРОКСИ
Прокси: 45.32.56.105:1385X с авторизацией Ek0G8F:GR0Fhj
Формат: http://username:password@host:port
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Прокси с авторизацией - правильный формат для Playwright
PROXIES = [
    {"server": "http://Ek0G8F:GR0Fhj@45.32.56.105:13851"},
    {"server": "http://Ek0G8F:GR0Fhj@45.32.56.105:13852"},
    {"server": "http://Ek0G8F:GR0Fhj@45.32.56.105:13853"},
]

ZH_RU_DICT = {
    "万公里": " тыс. км",
    "年": " г.",
    "北京": "Пекин",
    "奔驰": "Mercedes-Benz",
    "宝马": "BMW",
    "奥迪": "Audi",
    "保时捷": "Porsche",
    "路虎": "Land Rover",
    "揽胜": "Range Rover",
    "Model Y": "Tesla Model Y",
    "S 级": "S-Class",
    "舒适版": "Comfort",
    "豪华型": "Luxury",
    "运动型": "Sport",
    "自动": "АКПП",
}

def translate(text):
    for zh, ru in ZH_RU_DICT.items():
        text = text.replace(zh, ru)
    return text

async def parse_cars():
    print("=" * 60)
    print("ПАРСИНГ CHE168.COM - 10 АВТОМОБИЛЕЙ ЧЕРЕЗ ПРОКСИ")
    print("=" * 60)
    print(f"Прокси: {len(PROXIES)} шт")
    for i, p in enumerate(PROXIES):
        print(f"  [{i+1}] {p['server']}")
    print(f"Цель: 10 автомобилей")
    print("=" * 60)

    all_cars = []
    proxy_index = 0
    max_attempts = 15  # Максимум попыток

    async with async_playwright() as p:
        while len(all_cars) < 10 and proxy_index < max_attempts:
            proxy = PROXIES[proxy_index % len(PROXIES)]
            print(f"\n[Попытка {len(all_cars) + 1}] Прокси: {proxy['server']}")

            try:
                # Запускаем браузер с прокси на уровне launch
                browser = await p.chromium.launch(
                    proxy=proxy,
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )

                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                )
                page = await context.new_page()

                # Загружаем che168 - короткий таймаут
                print(f"  Загрузка che168.com...")
                await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(3)  # Ждем загрузки JS и контента

                # Собираем данные - ищем карточки авто
                car_data = await page.evaluate("""
                    () => {
                        const cars = [];

                        // Пробуем разные селекторы
                        const selectors = [
                            '[class*="car-item"]',
                            '[class*="car-card"]',
                            '[class*="vehicle"]',
                            '.car-list li',
                            '[data-type="car"]',
                            'a[href*="/dealer/"]'
                        ];

                        for (const sel of selectors) {
                            const els = document.querySelectorAll(sel);
                            els.forEach((el, i) => {
                                if (i < 20) {
                                    const text = el.innerText || '';
                                    const img = el.querySelector('img');
                                    const link = el.querySelector('a');
                                    if (text.length > 30 && text.includes('万')) {
                                        cars.push({
                                            text: text.replace(/\\s+/g, ' ').trim().substring(0, 300),
                                            img: img?.src || '',
                                            link: link?.href || ''
                                        });
                                    }
                                }
                            });
                            if (cars.length > 0) break;
                        }

                        // Если не нашли по селекторам - ищем по тексту
                        if (cars.length === 0) {
                            const all = document.querySelectorAll('*');
                            all.forEach(el => {
                                const text = el.innerText || '';
                                if (text.length > 50 && text.includes('万') && text.includes('年')) {
                                    const img = el.querySelector('img');
                                    const link = el.querySelector('a');
                                    cars.push({
                                        text: text.replace(/\\s+/g, ' ').trim().substring(0, 300),
                                        img: img?.src || '',
                                        link: link?.href || ''
                                    });
                                }
                            });
                        }

                        return cars.slice(0, 15);
                    }
                """)

                await context.close()
                await browser.close()

                print(f"  Найдено элементов: {len(car_data)}")

                # Обрабатываем авто
                for item in car_data:
                    if len(all_cars) >= 10:
                        break

                    text = item['text']
                    if not text or len(text) < 30:
                        continue

                    price_match = re.search(r'(\d+\.?\d*)\s*万', text)
                    price_cny = float(price_match.group(1)) * 10000 if price_match else 0

                    mileage_match = re.search(r'(\d+\.?\d*)\s*万公里', text)
                    mileage = float(mileage_match.group(1)) * 10000 if mileage_match else 0

                    year_match = re.search(r'(\d{4})-\d', text)
                    year = int(year_match.group(1)) if year_match else 0

                    if price_cny > 0:
                        all_cars.append({
                            "title_ru": translate(text[:120]),
                            "price_cny": price_cny,
                            "price_rub": round(price_cny * 13, 2),
                            "mileage_km": mileage,
                            "year": year,
                            "image": item['img'],
                            "url": item['link'],
                            "proxy": proxy['server'],
                        })

                print(f"  Всего авто: {len(all_cars)}/10")

            except Exception as e:
                error_msg = str(e)
                print(f"  ОШИБКА: {error_msg[:150]}")

                # Если прокси не работает - пробуем следующий
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    print(f"  -> Прокси не отвечает, переключаемся...")

            proxy_index += 1

            if len(all_cars) < 10:
                wait_time = 1
                print(f"  Ожидание {wait_time} сек...")
                await asyncio.sleep(wait_time)

    # Фильтруем дубликаты
    seen = set()
    unique_cars = []
    for car in all_cars:
        key = f"{car['price_cny']}_{car['mileage_km']}_{car['year']}"
        if key not in seen and len(unique_cars) < 10:
            seen.add(key)
            unique_cars.append(car)

    print("\n" + "=" * 60)
    print(f"ИТОГО: {len(unique_cars)} уникальных автомобилей")
    print("=" * 60)

    if len(unique_cars) == 0:
        print("ВНИМАНИЕ: Не удалось получить данные!")
        print("Возможные причины:")
        print("  1. Прокси не работают")
        print("  2. Сайт блокирует запросы")
        print("  3. Изменилась структура сайта")

    for i, car in enumerate(unique_cars):
        title_preview = car['title_ru'][:60].encode('cp1251', errors='replace').decode('cp1251')
        print(f"[{i+1}] {title_preview}... - {car['price_rub']:,.0f} руб")

    # Сохраняем JSON
    output_json = Path(__file__).parent / "che168_10_cars_result.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source": "che168.com",
            "total": len(unique_cars),
            "proxies_used": [p['server'] for p in PROXIES],
            "cars": unique_cars
        }, f, ensure_ascii=False, indent=2)

    # Генерируем HTML
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Автомобили из Китая - che168.com</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .info {{ background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
        .card {{ background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .img {{ width: 100%; height: 220px; object-fit: cover; background: #eee; }}
        .info-card {{ padding: 15px; }}
        .title {{ font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #333; }}
        .price {{ color: #e74c3c; font-size: 20px; font-weight: bold; margin: 10px 0; }}
        .details {{ color: #666; font-size: 14px; line-height: 1.6; }}
        .details div {{ margin: 5px 0; }}
        .proxy {{ font-size: 12px; color: #999; margin-top: 10px; }}
    </style>
</head>
<body>
    <h1>Автомобили из Китая (che168.com)</h1>
    <div class="info">
        <div><strong>Дата парсинга:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</div>
        <div><strong>Всего авто:</strong> {len(unique_cars)} шт</div>
        <div><strong>Прокси:</strong> {len(PROXIES)} шт (ротация)</div>
    </div>

    <div class="grid">
"""

    for c in unique_cars:
        img_err = "this.src='https://via.placeholder.com/400x220?text=No+Image'"
        html += f"""
        <div class="card">
            <img src="{c['image']}" onerror="{img_err}" class="img">
            <div class="info-card">
                <div class="title">{c['title_ru'][:80]}</div>
                <div class="price">{c['price_rub']:,.0f} ₽</div>
                <div class="details">
                    <div>Год: {c['year']}</div>
                    <div>Пробег: {c['mileage_km']:,.0f} км</div>
                    <div>Цена в Китае: {c['price_cny']:,.0f} CNY</div>
                </div>
                <div class="proxy">Proxy: {c['proxy']}</div>
            </div>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    output_html = Path(__file__).parent / "che168_10_cars_result.html"
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nJSON: {output_json}")
    print(f"HTML: {output_html}")

    return unique_cars

if __name__ == "__main__":
    asyncio.run(parse_cars())
