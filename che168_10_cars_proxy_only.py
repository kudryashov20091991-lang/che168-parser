"""
Парсер che168.com - 10 автомобилей СТРОГО через ПРОКСИ
БЕЗ прямого подключения - только через прокси!
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Прокси - 3 штуки с ротацией
PROXIES = [
    {"server": "http://45.32.56.105:13851", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "http://45.32.56.105:13852", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "http://45.32.56.105:13853", "username": "Ek0G8F", "password": "GR0Fhj"},
]

ZH_RU = {
    "万公里": " тыс. км", "年": " г.", "北京": "Пекин",
    "奔驰": "Mercedes-Benz", "宝马": "BMW", "奥迪": "Audi",
    "保时捷": "Porsche", "路虎": "Land Rover", "揽胜": "Range Rover",
}

def translate(t):
    for z, r in ZH_RU.items(): t = t.replace(z, r)
    return t

async def parse_strict_proxy():
    print("=" * 60)
    print("ПАРСИНГ CHE168.COM - СТРОГО ЧЕРЕЗ ПРОКСИ")
    print("=" * 60)
    for i, p in enumerate(PROXIES):
        print(f"[{i+1}] {p['server']} | {p['username']}:{p['password']}")
    print("=" * 60)

    all_cars = []
    max_attempts = 50  # Много попыток с разными прокси

    async with async_playwright() as pw:
        for attempt in range(max_attempts):
            if len(all_cars) >= 10:
                break

            proxy = PROXIES[attempt % len(PROXIES)]
            print(f"\n[Попытка {attempt+1}] {proxy['server']}")

            try:
                browser = await pw.chromium.launch(
                    proxy=proxy,
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )

                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                # Загрузка страницы
                await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(4)

                # Сбор данных
                cars = await page.evaluate("""() => {
                    const result = [];
                    const els = document.querySelectorAll('*');
                    els.forEach(el => {
                        const text = el.innerText || '';
                        if (text.length > 50 && text.includes('万') && text.includes('年')) {
                            const img = el.querySelector('img');
                            const link = el.querySelector('a');
                            result.push({
                                text: text.replace(/\\s+/g, ' ').substring(0, 300),
                                img: img?.src || '',
                                link: link?.href || ''
                            });
                        }
                    });
                    return result.slice(0, 20);
                }""")

                await context.close()
                await browser.close()

                print(f"  Найдено: {len(cars)}")

                for item in cars:
                    if len(all_cars) >= 10:
                        break
                    text = item['text']
                    if len(text) < 30:
                        continue

                    price_m = re.search(r'(\d+\.?\d*)\s*万', text)
                    price = float(price_m.group(1)) * 10000 if price_m else 0

                    mileage_m = re.search(r'(\d+\.?\d*)\s*万公里', text)
                    mileage = float(mileage_m.group(1)) * 10000 if mileage_m else 0

                    year_m = re.search(r'(\d{4})-\d', text)
                    year = int(year_m.group(1)) if year_m else 0

                    if price > 0:
                        all_cars.append({
                            "title_ru": translate(text[:120]),
                            "price_cny": price,
                            "price_rub": round(price * 13, 2),
                            "mileage_km": mileage,
                            "year": year,
                            "image": item['img'],
                            "url": item['link'],
                            "proxy": proxy['server'],
                        })

                print(f"  Всего: {len(all_cars)}/10")

            except Exception as e:
                err = str(e)[:100]
                print(f"  ОШИБКА: {err}")
                try:
                    await browser.close()
                except:
                    pass

            await asyncio.sleep(2)

    # Уникальные
    seen = set()
    unique = []
    for c in all_cars:
        key = f"{c['price_cny']}_{c['mileage_km']}_{c['year']}"
        if key not in seen and len(unique) < 10:
            seen.add(key)
            unique.append(c)

    print("\n" + "=" * 60)
    print(f"РЕЗУЛЬТАТ: {len(unique)} авто")
    print("=" * 60)

    for i, c in enumerate(unique):
        t = c['title_ru'][:60].encode('cp1251', 'replace').decode('cp1251')
        print(f"[{i+1}] {t}... - {c['price_rub']:,.0f} руб")

    # Сохранение
    ts = datetime.now()
    out_json = Path(__file__).parent / "che168_10_cars_final.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": ts.isoformat(),
            "source": "che168.com",
            "total": len(unique),
            "proxies": [p['server'] for p in PROXIES],
            "cars": unique
        }, f, ensure_ascii=False, indent=2)

    # HTML
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Автомобили из Китая</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
        .card {{ background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .img {{ width: 100%; height: 220px; object-fit: cover; }}
        .info {{ padding: 15px; }}
        .title {{ font-size: 16px; font-weight: bold; margin-bottom: 10px; }}
        .price {{ color: #e74c3c; font-size: 20px; font-weight: bold; }}
        .details {{ color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>Автомобили из Китая (che168.com)</h1>
    <p>Дата: {ts.strftime("%d.%m.%Y %H:%M")} | Всего: {len(unique)} шт | Прокси: {len(PROXIES)} шт</p>
    <div class="grid">
"""
    for c in unique:
        err = "this.src='https://via.placeholder.com/400x220?text=No+Image'"
        html += f"""
        <div class="card">
            <img src="{c['image']}" onerror="{err}" class="img">
            <div class="info">
                <div class="title">{c['title_ru'][:80]}</div>
                <div class="price">{c['price_rub']:,.0f} ₽</div>
                <div class="details">
                    <div>Год: {c['year']}</div>
                    <div>Пробег: {c['mileage_km']:,.0f} км</div>
                    <div>Цена: {c['price_cny']:,.0f} CNY</div>
                </div>
                <div style="font-size:12px;color:#999;margin-top:10px">Proxy: {c['proxy']}</div>
            </div>
        </div>
"""
    html += "\n    </div>\n</body>\n</html>"

    out_html = Path(__file__).parent / "che168_10_cars_final.html"
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nJSON: {out_json}")
    print(f"HTML: {out_html}")

    return unique

if __name__ == "__main__":
    asyncio.run(parse_strict_proxy())
