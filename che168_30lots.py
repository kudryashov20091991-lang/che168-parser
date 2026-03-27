"""
Парсер che168.com - 30 лотов
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

async def parse_30():
    print("Загрузка страницы...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(5)

        # Скроллим страницу для загрузки контента
        for i in range(3):
            await page.evaluate(f"window.scrollTo(0, {(i+1) * 500})")
            await asyncio.sleep(1)

        # Собираем все элементы с текстом
        all_texts = await page.evaluate("""
            () => {
                const results = [];
                const elements = document.querySelectorAll('a[href*="/dealer/"], [class*="car"], [class*="item"], li, div');

                elements.forEach(el => {
                    const text = (el.innerText || '').replace(/\\s+/g, ' ').trim();
                    if (text.length > 40 && text.includes('万') && text.includes('年')) {
                        const img = el.querySelector('img');
                        const link = el.querySelector('a');
                        results.push({
                            text: text.substring(0, 250),
                            img: img?.src || '',
                            link: link?.href || ''
                        });
                    }
                });
                return results;
            }
        """)

        await browser.close()

        # Обрабатываем
        seen = set()
        cars = []
        for item in all_texts:
            text = item['text']
            if not text:
                continue

            price_match = re.search(r'(\d+\.?\d*)\s*万', text)
            if not price_match:
                continue

            price_cny = float(price_match.group(1)) * 10000

            mileage_match = re.search(r'(\d+\.?\d*)\s*万公里', text)
            mileage = float(mileage_match.group(1)) * 10000 if mileage_match else 0

            year_match = re.search(r'(\d{4})-\d', text)
            year = int(year_match.group(1)) if year_match else 0

            if price_cny > 0:
                key = f"{price_cny}_{mileage}_{year}"
                if key not in seen and len(cars) < 30:
                    seen.add(key)
                    cars.append({
                        "title_ru": translate(text[:150]),
                        "price_cny": price_cny,
                        "price_rub": round(price_cny * 13, 2),
                        "mileage_km": mileage,
                        "year": year,
                        "image": item['img'],
                        "url": item['link'],
                    })

        print(f"Найдено: {len(cars)} авто")

        for i, car in enumerate(cars[:10]):
            title = car['title_ru'][:70].encode('cp1251', errors='replace').decode('cp1251')
            print(f"[{i+1}] {title}... - {car['price_rub']:,.0f} RUB")

        # Сохраняем
        output_dir = Path(__file__).parent
        with open(output_dir / "che168_30_cars.json", "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "source": "che168.com",
                "total": len(cars),
                "cars": cars
            }, f, ensure_ascii=False, indent=2)

        # HTML
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Авто из Китая - che168.com</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f9f9f9; }}
        h1 {{ color: #333; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }}
        .card {{ background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }}
        .img {{ width: 100%; height: 200px; object-fit: cover; }}
        .info {{ padding: 15px; }}
        .title {{ font-weight: bold; margin-bottom: 10px; min-height: 40px; }}
        .price {{ color: #e74c3c; font-size: 18px; font-weight: bold; }}
        .meta {{ color: #666; font-size: 13px; margin-top: 8px; }}
    </style>
</head>
<body>
    <h1>Автомобили из Китая (che168.com)</h1>
    <p>Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")} | Всего: {len(cars)} авто</p>
    <div class="grid">
"""
        for c in cars:
            html += f"""
        <div class="card">
            <img src="{c['image']}" onerror="this.src='https://via.placeholder.com/400x200'" class="img">
            <div class="info">
                <div class="title">{c['title_ru'][:80]}</div>
                <div class="price">{c['price_rub']:,.0f} ₽</div>
                <div class="meta">
                    <div>Год: {c['year']} | Пробег: {c['mileage_km']:,.0f} км</div>
                    <div>Цена: {c['price_cny']:,.0f} CNY</div>
                </div>
            </div>
        </div>
"""
        html += """
    </div>
</body>
</html>
"""
        with open(output_dir / "che168_30_cars.html", "w", encoding="utf-8") as f:
            f.write(html)

        print(f"Файлы: che168_30_cars.json, che168_30_cars.html")
        return cars

if __name__ == "__main__":
    asyncio.run(parse_30())
