"""
Парсер dongchedi.com - добиваем до 30 лотов
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

async def parse_dongchedi():
    print("Парсинг dongchedi.com...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # Главная с авто
        await page.goto("https://www.dongchedi.com/auto", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(4)

        # Скроллим
        for i in range(3):
            await page.evaluate(f"window.scrollTo(0, {(i+1) * 400})")
            await asyncio.sleep(0.5)

        items = await page.evaluate("""
            () => {
                const results = [];
                const all = document.querySelectorAll('*');
                all.forEach(el => {
                    const text = (el.innerText || '').replace(/\\s+/g, ' ').trim();
                    if (text.length > 30 && (text.includes('万') || text.includes('¥'))) {
                        const img = el.querySelector('img');
                        const link = el.querySelector('a');
                        results.push({
                            text: text.substring(0, 200),
                            img: img?.src || '',
                            link: link?.href || ''
                        });
                    }
                });
                return results.slice(0, 50);
            }
        """)

        await browser.close()

    # Обрабатываем
    seen = set()
    cars = []
    for item in items:
        text = item['text']
        if not text or '万' not in text:
            continue

        # Цена
        price_match = re.search(r'[¥￥]\s*(\d+\.?\d*)\s*万', text)
        if not price_match:
            price_match = re.search(r'(\d+\.?\d*)\s*万', text)
        if not price_match:
            continue

        price_cny = float(price_match.group(1)) * 10000

        # Пробег
        mileage_match = re.search(r'(\d+\.?\d*)\s*万公里', text)
        mileage = float(mileage_match.group(1)) * 10000 if mileage_match else 0

        # Год
        year_match = re.search(r'(\d{4})', text)
        year = int(year_match.group(1)) if year_match else 2020

        if price_cny > 50000:  # Минимальная цена
            key = f"{price_cny}_{mileage}_{year}"
            if key not in seen and len(cars) < 30:
                seen.add(key)
                cars.append({
                    "title_ru": translate(text[:120]),
                    "price_cny": price_cny,
                    "price_rub": round(price_cny * 13, 2),
                    "mileage_km": mileage,
                    "year": year,
                    "image": item['img'],
                    "url": item['link'],
                })

    print(f"Найдено: {len(cars)} авто")
    return cars

if __name__ == "__main__":
    cars = asyncio.run(parse_dongchedi())
    print(f"Готово: {len(cars)} автомобилей")
