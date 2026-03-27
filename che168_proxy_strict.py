"""
Парсер che168.com - 10 автомобилей ТОЛЬКО через прокси
Прокси: 45.32.56.105:13851/52/53
Auth: Ek0G8F:GR0Fhj

ЗАПРЕЩЕНО: Парсинг без прокси
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Прокси - правильный формат для Playwright
PROXIES = [
    {
        "server": "http://45.32.56.105:13851",
        "username": "Ek0G8F",
        "password": "GR0Fhj"
    },
    {
        "server": "http://45.32.56.105:13852",
        "username": "Ek0G8F",
        "password": "GR0Fhj"
    },
    {
        "server": "http://45.32.56.105:13853",
        "username": "Ek0G8F",
        "password": "GR0Fhj"
    },
]

ZH_RU = {
    "万公里": " тыс. км", "年": " г.", "北京": "Пекин",
    "奔驰": "Mercedes-Benz", "宝马": "BMW", "奥迪": "Audi",
    "保时捷": "Porsche", "路虎": "Land Rover", "揽胜": "Range Rover",
    "Model Y": "Model Y", "S 级": "S-Class", "自动": "АКПП",
}

def translate(t):
    for z, r in ZH_RU.items(): t = t.replace(z, r)
    return t

async def parse():
    print("=" * 60)
    print("ПАРСИНГ CHE168.COM - ТОЛЬКО ЧЕРЕЗ ПРОКСИ")
    print("=" * 60)
    for i, p in enumerate(PROXIES):
        print(f"[{i+1}] {p['server']} | {p['username']}:{p['password']}")
    print("=" * 60)

    cars = []
    proxy_idx = 0
    max_tries = 15

    async with async_playwright() as p:
        while len(cars) < 10 and proxy_idx < max_tries:
            proxy = PROXIES[proxy_idx % len(PROXIES)]
            print(f"\n[Попытка {len(cars)+1}] {proxy['server']}")

            try:
                browser = await p.chromium.launch(
                    proxy=proxy,
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                # Проверка IP
                try:
                    await page.goto("https://api.ipify.org?format=json", timeout=10000)
                    content = await page.content()
                    ip = re.search(r'\d+\.\d+\.\d+\.\d+', content)
                    if ip: print(f"  IP: {ip.group()}")
                except:
                    print("  IP: не проверен")

                # Загрузка che168
                print("  Загрузка che168.com/beijing/...")
                await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(4)

                # Сбор данных
                data = await page.evaluate("""() => {
                    const cars = [];
                    const all = document.querySelectorAll('*');
                    all.forEach(el => {
                        const t = el.innerText || '';
                        if (t.length > 50 && t.includes('万') && t.includes('年')) {
                            const img = el.querySelector('img');
                            const a = el.querySelector('a');
                            cars.push({
                                t: t.replace(/\\s+/g, ' ').slice(0, 300),
                                i: img?.src || '',
                                l: a?.href || ''
                            });
                        }
                    });
                    return cars.slice(0, 20);
                }""")

                await context.close()
                await browser.close()

                print(f"  Найдено: {len(data)}")

                for item in data:
                    if len(cars) >= 10: break
                    t = item['t']
                    if len(t) < 30: continue

                    price = re.search(r'(\d+\.?\d*)\s*万', t)
                    price_cny = float(price.group(1)) * 10000 if price else 0

                    mil = re.search(r'(\d+\.?\d*)\s*万公里', t)
                    mileage = float(mil.group(1)) * 10000 if mil else 0

                    yr = re.search(r'(\d{4})-\d', t)
                    year = int(yr.group(1)) if yr else 0

                    if price_cny > 0:
                        cars.append({
                            "title_ru": translate(t[:120]),
                            "price_cny": price_cny,
                            "price_rub": round(price_cny * 13, 2),
                            "mileage_km": mileage,
                            "year": year,
                            "image": item['i'],
                            "url": item['l'],
                            "proxy": proxy['server']
                        })

                print(f"  Всего: {len(cars)}/10")

            except Exception as e:
                err = str(e)[:120]
                print(f"  ОШИБКА: {err}")
                try: await browser.close()
                except: pass

            proxy_idx += 1
            if len(cars) < 10:
                await asyncio.sleep(2)

    # Уникальные
    seen, unique = set(), []
    for c in cars:
        k = f"{c['price_cny']}_{c['mileage_km']}_{c['year']}"
        if k not in seen and len(unique) < 10:
            seen.add(k)
            unique.append(c)

    print("\n" + "=" * 60)
    print(f"ИТОГО: {len(unique)} авто")
    print("=" * 60)

    for i, c in enumerate(unique):
        t = c['title_ru'][:60].encode('cp1251', 'replace').decode('cp1251')
        print(f"[{i+1}] {t}... - {c['price_rub']:,.0f} руб")

    # Сохранение
    ts = datetime.now().isoformat()
    out_json = Path(__file__).parent / "che168_10_cars_proxy.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"timestamp": ts, "source": "che168.com", "total": len(unique), "cars": unique}, f, ensure_ascii=False, indent=2)

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Авто из Китая</title>
    <style>body{{font-family:Arial;padding:20px;background:#f5f5f5}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px}}.card{{background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1)}}.img{{width:100%;height:220px;object-fit:cover}}.info{{padding:15px}}.title{{font-size:16px;font-weight:bold;margin-bottom:10px}}.price{{color:#e74c3c;font-size:20px;font-weight:bold}}.details{{color:#666;font-size:14px}}</style></head>
    <body><h1>Автомобили из Китая (che168.com)</h1><p>Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")} | Всего: {len(unique)}</p><div class="grid">"""

    for c in unique:
        html += f"""<div class="card"><img src="{c['image']}" onerror="this.src='https://via.placeholder.com/400x220'"><div class="info"><div class="title">{c['title_ru'][:80]}</div><div class="price">{c['price_rub']:,.0f} ₽</div><div class="details"><div>Год: {c['year']}</div><div>Пробег: {c['mileage_km']:,.0f} км</div><div>Цена: {c['price_cny']:,.0f} CNY</div></div></div></div>"""

    html += "</div></body></html>"
    out_html = Path(__file__).parent / "che168_10_cars_proxy.html"
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nJSON: {out_json}")
    print(f"HTML: {out_html}")
    return unique

if __name__ == "__main__":
    asyncio.run(parse())
