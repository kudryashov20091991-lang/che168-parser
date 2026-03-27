"""
Парсер che168.com - 10 автомобилей через ПРОКСИ
Версия 2: с быстрой проверкой прокси перед парсингом
"""

import asyncio
import json
import re
import requests
from datetime import datetime
from pathlib import Path

# Сначала проверяем прокси через requests с таймаутом
PROXIES_RAW = [
    {"host": "45.32.56.105", "port": "13851", "user": "Ek0G8F", "pass": "GR0Fhj"},
    {"host": "45.32.56.105", "port": "13852", "user": "Ek0G8F", "pass": "GR0Fhj"},
    {"host": "45.32.56.105", "port": "13853", "user": "Ek0G8F", "pass": "GR0Fhj"},
]

def check_proxy_fast(proxy):
    """Быстрая проверка прокси через requests (5 сек)"""
    proxies = {
        "http": f"http://{proxy['user']}:{proxy['pass']}@{proxy['host']}:{proxy['port']}",
        "https": f"http://{proxy['user']}:{proxy['pass']}@{proxy['host']}:{proxy['port']}",
    }
    try:
        resp = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            ip = data.get('origin', 'unknown')
            return True, ip
    except:
        pass
    return False, None

def check_all_proxies():
    """Проверяем все прокси быстро"""
    print("=" * 60)
    print("ПРОВЕРКА ПРОКСИ")
    print("=" * 60)

    working = []
    for i, p in enumerate(PROXIES_RAW):
        addr = f"{p['host']}:{p['port']}"
        print(f"[{i+1}] {addr}...", end=" ", flush=True)
        ok, ip = check_proxy_fast(p)
        if ok:
            print(f"OK (IP: {ip})")
            working.append(p)
        else:
            print("FAIL")

    print(f"\nРабочих прокси: {len(working)} из {len(PROXIES_RAW)}")
    print("=" * 60)
    return working

# Если прокси не работают - используем прямое подключение
async def parse_with_playwright(proxies_working):
    from playwright.async_api import async_playwright

    # Формируем прокси для Playwright
    if proxies_working:
        PROXIES_PW = [
            {"server": f"http://{p['user']}:{p['pass']}@{p['host']}:{p['port']}"}
            for p in proxies_working
        ]
        print(f"Используем прокси: {len(PROXIES_PW)} шт")
    else:
        PROXIES_PW = []
        print("ВНИМАНИЕ: Прокси не работают, используем прямое подключение!")

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

    print("\n" + "=" * 60)
    print("ПАРСИНГ CHE168.COM")
    print("=" * 60)

    all_cars = []
    proxy_index = 0
    max_attempts = 20

    async with async_playwright() as p:
        while len(all_cars) < 10 and proxy_index < max_attempts:
            use_proxy = len(PROXIES_PW) > 0
            proxy = PROXIES_PW[proxy_index % len(PROXIES_PW)] if use_proxy else None

            if use_proxy:
                print(f"\n[Попытка {len(all_cars)+1}] Прокси: {proxy['server'][:40]}...")
            else:
                print(f"\n[Попытка {len(all_cars)+1}] Прямое подключение")

            try:
                if use_proxy:
                    browser = await p.chromium.launch(
                        proxy=proxy,
                        headless=True,
                        args=['--no-sandbox', '--disable-setuid-sandbox']
                    )
                else:
                    browser = await p.chromium.launch(
                        headless=True,
                        args=['--no-sandbox', '--disable-setuid-sandbox']
                    )

                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                # Короткий таймаут для загрузки
                await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(3)

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
                                    text: text.replace(/\\s+/g, ' ').trim().substring(0, 300),
                                    img: img?.src || '',
                                    link: link?.href || ''
                                });
                            }
                        });
                        return cars.slice(0, 20);
                    }
                """)

                await context.close()
                await browser.close()

                print(f"  Найдено: {len(car_data)} элементов")

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
                            "proxy": proxy['server'] if proxy else "direct",
                        })

                print(f"  Всего: {len(all_cars)}/10")

            except Exception as e:
                error = str(e)[:100]
                print(f"  Ошибка: {error}")
                try:
                    await browser.close()
                except:
                    pass

            proxy_index += 1
            if len(all_cars) < 10:
                await asyncio.sleep(1)

    # Фильтруем дубликаты
    seen = set()
    unique_cars = []
    for car in all_cars:
        key = f"{car['price_cny']}_{car['mileage_km']}_{car['year']}"
        if key not in seen and len(unique_cars) < 10:
            seen.add(key)
            unique_cars.append(car)

    print("\n" + "=" * 60)
    print(f"ИТОГО: {len(unique_cars)} авто")
    print("=" * 60)

    for i, car in enumerate(unique_cars):
        title = car['title_ru'][:60].encode('cp1251', errors='replace').decode('cp1251')
        price = car['price_rub']
        print(f"[{i+1}] {title}... - {price:,.0f} руб")

    # Сохраняем
    output_json = Path(__file__).parent / "che168_10_cars.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source": "che168.com",
            "total": len(unique_cars),
            "proxies_checked": len(proxies_working),
            "cars": unique_cars
        }, f, ensure_ascii=False, indent=2)

    # HTML
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Автомобили из Китая - che168.com</title>
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
    <p>Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")} | Всего: {len(unique_cars)} шт</p>
    <div class="grid">
"""
    for c in unique_cars:
        img_err = "this.src='https://via.placeholder.com/400x220?text=No+Image'"
        html += f"""
        <div class="card">
            <img src="{c['image']}" onerror="{img_err}" class="img">
            <div class="info">
                <div class="title">{c['title_ru'][:80]}</div>
                <div class="price">{c['price_rub']:,.0f} ₽</div>
                <div class="details">
                    <div>Год: {c['year']}</div>
                    <div>Пробег: {c['mileage_km']:,.0f} км</div>
                    <div>Цена: {c['price_cny']:,.0f} CNY</div>
                </div>
            </div>
        </div>
"""
    html += "\n    </div>\n</body>\n</html>"

    output_html = Path(__file__).parent / "che168_10_cars.html"
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nJSON: {output_json}")
    print(f"HTML: {output_html}")

    return unique_cars

if __name__ == "__main__":
    # 1. Быстрая проверка прокси
    working_proxies = check_all_proxies()

    # 2. Парсинг
    import asyncio
    asyncio.run(parse_with_playwright(working_proxies))
