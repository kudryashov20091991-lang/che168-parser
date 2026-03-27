"""
Парсер che168.com - улучшенная версия с уникальными авто
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
    "特斯拉": "Tesla",
    "雷克萨斯": "Lexus",
    "丰田": "Toyota",
    "本田": "Honda",
    "日产": "Nissan",
    "马自达": "Mazda",
    "款": "",
    "舒适版": "Comfort",
    "豪华型": "Luxury",
    "运动型": "Sport",
}

def translate(text):
    for zh, ru in ZH_RU_DICT.items():
        text = text.replace(zh, ru)
    return text

async def parse_cars():
    print("Запуск парсера...")
    seen_prices = set()
    cars = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        print("Загрузка страницы...")
        await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        # Скроллим страницу
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(1)

        # Собираем все элементы с ценами
        items = await page.evaluate("""
            () => {
                const results = [];
                // Ищем карточки авто
                document.querySelectorAll('[class*="car"], [class*="item"], li, a').forEach(el => {
                    const text = el.innerText || '';
                    if (text.includes('万') && text.includes('年') && text.length > 30) {
                        const img = el.querySelector('img');
                        const link = el.querySelector('a');
                        results.push({
                            text: text.replace(/\\s+/g, ' ').trim(),
                            img: img?.src || img?.dataset?.src || '',
                            link: link?.href || ''
                        });
                    }
                });
                return results;
            }
        """)

        await browser.close()

        print(f"Найдено элементов: {len(items)}")

        # Обрабатываем, убираем дубликаты по цене
        for item in items:
            text = item['text']
            if not text or len(text) < 30:
                continue

            # Извлекаем цену (последнее число с 万)
            price_matches = re.findall(r'(\d+\.?\d*)\s*万', text)
            if not price_matches:
                continue

            price_cny = float(price_matches[-1]) * 10000
            price_key = int(price_cny / 1000)  # Ключ для проверки дубликатов

            if price_key in seen_prices or len(cars) >= 15:
                continue
            seen_prices.add(price_key)

            # Извлекаем данные
            mileage_match = re.search(r'(\d+\.?\d*)\s*万公里', text)
            mileage = float(mileage_match.group(1)) * 10000 if mileage_match else 0

            year_match = re.search(r'(\d{4})-\d{1,2}', text)
            year = int(year_match.group(1)) if year_match else 0

            # Чищем заголовок - берем первую часть до повторений
            title_clean = text[:150]
            if '新上架' in title_clean:
                title_clean = title_clean.split('新上架')[0]

            cars.append({
                "title_ru": translate(title_clean),
                "price_cny": price_cny,
                "price_rub": round(price_cny * 13, 2),
                "mileage_km": mileage,
                "year": year,
                "image": item['img'],
                "url": item['link'] if item['link'] and item['link'].startswith('http') else '',
                "location": "Пекин, Китай",
            })

        print(f"Уникальных авто: {len(cars)}")

        # Вывод результатов
        for i, car in enumerate(cars, 1):
            title_preview = car['title_ru'][:60].encode('cp1251', errors='replace').decode('cp1251')
            print(f"\n[{i}] {title_preview}...")
            print(f"    Cena: {car['price_rub']:,.0f} RUB | Probeg: {car['mileage_km']:,.0f} km | God: {car['year']}")

        # Сохраняем
        output = Path(__file__).parent / "che168_cars_final.json"
        with open(output, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "source": "che168.com/beijing/",
                "total_cars": len(cars),
                "cars": cars
            }, f, ensure_ascii=False, indent=2)

        # HTML
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>Авто из Китая</title>
<style>body{{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}}.card{{background:white;border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}.img{{width:100%;height:200px;object-fit:cover;background:#eee}}.info{{padding:15px}}.title{{font-size:16px;font-weight:bold;margin-bottom:10px}}.price{{color:#e74c3c;font-size:20px;font-weight:bold;margin:10px 0}}.details{{color:#666;font-size:14px;line-height:1.6}}</style>
</head><body>
<h1>Автомобили из Китая (che168.com)</h1>
<p>Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")} | Всего: {len(cars)}</p>
<div class="grid">
"""
        for c in cars:
            img = c['image'] if c['image'] else 'https://via.placeholder.com/400x200'
            html += f"""<div class="card">
<img src="{img}" class="img" onerror="this.src='https://via.placeholder.com/400x200'">
<div class="info">
<div class="title">{c['title_ru'][:80]}</div>
<div class="price">{c['price_rub']:,.0f} ₽</div>
<div class="details">
<div>Год: {c['year']}</div><div>Пробег: {c['mileage_km']:,.0f} км</div><div>Цена: {c['price_cny']:,.0f} CNY</div>
</div></div></div>
"""
        html += "</div></body></html>"

        html_file = Path(__file__).parent / "che168_cars_final.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"\nСохранено: {output}, {html_file}")
        return cars

if __name__ == "__main__":
    asyncio.run(parse_cars())
