"""
Парсер che168.com через бесплатные рабочие прокси
"""

import asyncio
import json
import re
import requests
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

def get_free_proxies():
    """Получить список бесплатных прокси"""
    proxies = []
    try:
        resp = requests.get(
            "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http&proxy_format=ipport&format=json",
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            for p in data.get("proxies", [])[:30]:
                proxies.append({"server": f"http://{p['ip']}:{p['port']}"})
    except:
        pass
    return proxies

ZH_RU = {
    "万公里": " тыс. км", "年": " г.", "北京": "Пекин",
    "奔驰": "Mercedes-Benz", "宝马": "BMW", "奥迪": "Audi",
    "保时捷": "Porsche", "路虎": "Land Rover",
}

def translate(t):
    for z, r in ZH_RU.items(): t = t.replace(z, r)
    return t

async def parse_with_free_proxies():
    print("=" * 60)
    print("ПАРСИНГ CHE168.COM - БЕСПЛАТНЫЕ ПРОКСИ")
    print("=" * 60)

    proxies = get_free_proxies()
    print(f"Найдено прокси: {len(proxies)}")
    for i, p in enumerate(proxies[:5]):
        print(f"  [{i+1}] {p['server']}")
    print("...")
    print("=" * 60)

    all_cars = []
    proxy_idx = 0

    async with async_playwright() as pw:
        while len(all_cars) < 10 and proxy_idx < len(proxies):
            proxy = proxies[proxy_idx]
            print(f"\n[Попытка {proxy_idx+1}] {proxy['server']}")

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

                await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=25000)
                await asyncio.sleep(4)

                cars = await page.evaluate("""() => {
                    const result = [];
                    document.querySelectorAll('*').forEach(el => {
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
                print(f"  ОШИБКА: {str(e)[:80]}")
                try:
                    await browser.close()
                except:
                    pass

            proxy_idx += 1
            await asyncio.sleep(1)

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
    out_json = Path(__file__).parent / "che168_free_proxy.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": ts.isoformat(),
            "source": "che168.com",
            "total": len(unique),
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
    <p>Дата: {ts.strftime("%d.%m.%Y %H:%M")} | Всего: {len(unique)} шт</p>
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
                <div style="font-size:12px;color:#999">Proxy: {c['proxy']}</div>
            </div>
        </div>
"""
    html += "\n    </div>\n</body>\n</html>"

    out_html = Path(__file__).parent / "che168_free_proxy.html"
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nJSON: {out_json}")
    print(f"HTML: {out_html}")
    return unique

if __name__ == "__main__":
    asyncio.run(parse_with_free_proxies())
