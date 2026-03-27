"""
Парсер che168.com без прокси (прокси не работают)
30 автомобилей для выгрузки на сайт
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
}

def translate(text):
    for zh, ru in ZH_RU_DICT.items():
        text = text.replace(zh, ru)
    return text

async def parse_direct():
    print("=" * 60)
    print("ПАРСИНГ CHE168.COM (прямое подключение)")
    print("Прокси не работают - все таймауты")
    print("=" * 60)

    all_cars = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # Загружаем страницу
        print("Загрузка страницы...")
        await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5)

        # Собираем данные
        print("Сбор данных...")
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
                return cars.slice(0, 50);
            }
        """)

        await browser.close()

        # Обрабатываем
        seen = set()
        for item in car_data:
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
                key = f"{price_cny}_{mileage}_{year}"
                if key not in seen and len(all_cars) < 30:
                    seen.add(key)
                    all_cars.append({
                        "title_ru": translate(text[:120]),
                        "price_cny": price_cny,
                        "price_rub": round(price_cny * 13, 2),
                        "mileage_km": mileage,
                        "year": year,
                        "image": item['img'],
                        "url": item['link'],
                    })

        print(f"Найдено: {len(all_cars)} авто")

        # Вывод
        for i, car in enumerate(all_cars[:10]):
            title = car['title_ru'][:60].encode('cp1251', errors='replace').decode('cp1251')
            print(f"[{i+1}] {title}... - {car['price_rub']:,.0f} RUB")

    # Сохраняем
    output_json = Path(__file__).parent / "che168_30_cars.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source": "che168.com",
            "total": len(all_cars),
            "note": "Прокси не работают (таймауты), спаршено напрямую",
            "cars": all_cars
        }, f, ensure_ascii=False, indent=2)

    # HTML
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Автомобили из Китая</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .info {{ background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
        .card {{ background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-5px); }}
        .img {{ width: 100%; height: 220px; object-fit: cover; background: #eee; }}
        .info-card {{ padding: 15px; }}
        .title {{ font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #333; min-height: 40px; }}
        .price {{ color: #e74c3c; font-size: 20px; font-weight: bold; margin: 10px 0; }}
        .details {{ color: #666; font-size: 14px; line-height: 1.6; }}
        .badge {{ display: inline-block; background: #3498db; color: #fff; padding: 3px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; }}
    </style>
</head>
<body>
    <h1>🚗 Автомобили из Китая (che168.com)</h1>
    <div class="info">
        <div><strong>Дата:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</div>
        <div><strong>Всего:</strong> {len(all_cars)} автомобилей</div>
        <div><strong>Источник:</strong> che168.com (Пекин)</div>
    </div>

    <div class="grid">
"""

    for c in all_cars:
        img_err = "this.src='https://via.placeholder.com/400x220?text=No+Image'"
        html += f"""
        <div class="card">
            <img src="{c['image']}" onerror="{img_err}" class="img">
            <div class="info-card">
                <div class="title">{c['title_ru'][:80]}</div>
                <div class="price">{c['price_rub']:,.0f} ₽</div>
                <div class="details">
                    <div><span class="badge">Год</span> {c['year']}</div>
                    <div><span class="badge">Пробег</span> {c['mileage_km']:,.0f} км</div>
                    <div><span class="badge">Цена</span> {c['price_cny']:,.0f} CNY</div>
                </div>
            </div>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    output_html = Path(__file__).parent / "che168_30_cars.html"
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nJSON: {output_json}")
    print(f"HTML: {output_html}")
    print(f"\nВсего: {len(all_cars)} автомобилей")

    return all_cars

if __name__ == "__main__":
    asyncio.run(parse_direct())
