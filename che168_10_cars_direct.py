"""
Парсер che168.com - 10 автомобилей БЕЗ прокси (прямое подключение)
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

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
    print("ПАРСИНГ CHE168.COM - 10 АВТОМОБИЛЕЙ (БЕЗ ПРОКСИ)")
    print("=" * 60)

    all_cars = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        print("\nЗагрузка che168.com/beijing/...")
        try:
            await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(4)
            print("Страница загружена")
        except Exception as e:
            print(f"Ошибка загрузки: {str(e)[:100]}")
            await browser.close()
            return []

        # Собираем данные
        car_data = await page.evaluate("""
            () => {
                const cars = [];
                const all = document.querySelectorAll('*');
                all.forEach(el => {
                    const text = el.innerText || '';
                    if (text.length > 50 && text.includes('万') && text.includes('年')) {
                        const img = el.querySelector('img');
                        const link = el.querySelector('a');
                        cars.push({
                            text: text.replace(/\\s+/g, ' ').trim().substring(0, 200),
                            img: img?.src || '',
                            link: link?.href || ''
                        });
                    }
                });
                return cars.slice(0, 15);
            }
        """)

        await browser.close()

        print(f"Найдено элементов: {len(car_data)}")

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
                })

        print(f"Обработано авто: {len(all_cars)}")

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

    for i, car in enumerate(unique_cars):
        title_preview = car['title_ru'][:60].encode('cp1251', errors='replace').decode('cp1251')
        price = car['price_rub']
        print(f"[{i+1}] {title_preview}... - {price:,.0f} rub")

    # Сохраняем JSON
    output_json = Path(__file__).parent / "che168_10_cars_direct.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source": "che168.com",
            "total": len(unique_cars),
            "proxy": "direct (no proxy)",
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
    </style>
</head>
<body>
    <h1>Автомобили из Китая (che168.com)</h1>
    <div class="info">
        <div><strong>Дата парсинга:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</div>
        <div><strong>Всего авто:</strong> {len(unique_cars)} шт</div>
        <div><strong>Подключение:</strong> Прямое (без прокси)</div>
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
            </div>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    output_html = Path(__file__).parent / "che168_10_cars_direct.html"
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nJSON: {output_json}")
    print(f"HTML: {output_html}")

    return unique_cars

if __name__ == "__main__":
    asyncio.run(parse_cars())
