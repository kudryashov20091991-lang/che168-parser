"""
Парсер che168.com с повторными попытками
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
}

def translate(text):
    for zh, ru in ZH_RU_DICT.items():
        text = text.replace(zh, ru)
    return text

async def parse_with_retry():
    print("Запуск парсера...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Пробуем несколько раз
        for attempt in range(3):
            try:
                print(f"Попытка {attempt + 1}...")
                await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(5)

                # Проверяем есть ли контент
                content = await page.content()
                if len(content) > 10000:
                    print("Страница загружена успешно!")
                    break
            except Exception as e:
                print(f"Ошибка: {e}")
                if attempt < 2:
                    await asyncio.sleep(5)

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
                return cars.slice(0, 20);
            }
        """)

        await browser.close()

        # Обрабатываем
        cars = []
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

            if price_cny > 0 and len(cars) < 15:
                cars.append({
                    "title_ru": translate(text[:120]),
                    "price_cny": price_cny,
                    "price_rub": round(price_cny * 13, 2),
                    "mileage_km": mileage,
                    "year": year,
                    "image": item['img'],
                    "url": item['link'],
                })

        print(f"\nНайдено авто: {len(cars)}")

        # Сохраняем
        output = Path(__file__).parent / "che168_cars_final.json"
        with open(output, "w", encoding="utf-8") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "cars": cars}, f, ensure_ascii=False, indent=2)

        # HTML
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Авто из Китая</title>
<style>.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}}.card{{border:1px solid #ddd;border-radius:8px;overflow:hidden}}.img{{width:100%;height:200px;object-fit:cover}}.info{{padding:15px}}.price{{color:#e74c3c;font-size:18px;font-weight:bold}}</style>
</head><body>
<h1>Автомобили из Китая (che168.com)</h1>
<p>Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")}</p>
<div class="grid">
"""
        for c in cars:
            html += f"""<div class="card">
<img src="{c['image']}" onerror="this.src='https://via.placeholder.com/400x200'" class="img">
<div class="info">
<div style="font-weight:bold;margin-bottom:10px">{c['title_ru'][:80]}</div>
<div class="price">{c['price_rub']:,.0f} ₽</div>
<div style="color:#666;font-size:14px;margin-top:10px">
<div>Год: {c['year']}</div><div>Пробег: {c['mileage_km']:,.0f} км</div><div>Цена: {c['price_cny']:,.0f} CNY</div>
</div></div></div>
"""
        html += "</div></body></html>"

        html_file = Path(__file__).parent / "che168_cars_final.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"JSON: {output}")
        print(f"HTML: {html_file}")
        return cars

if __name__ == "__main__":
    asyncio.run(parse_with_retry())
