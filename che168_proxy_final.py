"""
Парсер che168.com с ПРОКСИ авторизацией
3 прокси, по 10 запросов с каждого = 30 лотов
Интервал: 1 минута между запросами
"""
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Прокси с авторизацией (формат: host:port:username:password)
PROXIES = [
    "45.32.56.105:13851:Ek0G8F:GR0Fhj",
    "45.32.56.105:13852:Ek0G8F:GR0Fhj",
    "45.32.56.105:13853:Ek0G8F:GR0Fhj",
]

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

async def parse_with_proxy_rotation():
    print("=" * 60)
    print("ПАРСИНГ CHE168.COM С ПРОКСИ РОТАЦИЕЙ")
    print("=" * 60)
    print(f"Прокси: {len(PROXIES)} шт")
    print(f"Цель: 30 автомобилей (по 10 с каждого прокси)")
    print(f"Интервал: 60 секунд между запросами")
    print("=" * 60)

    all_cars = []
    proxy_index = 0
    requests_per_proxy = 10
    total_requests = len(PROXIES) * requests_per_proxy

    async with async_playwright() as p:
        for req_num in range(total_requests):
            # Выбираем прокси по кругу
            proxy_str = PROXIES[proxy_index]
            proxy_parts = proxy_str.split(":")
            proxy_server = f"http://{proxy_parts[0]}:{proxy_parts[1]}"
            proxy_username = proxy_parts[2]
            proxy_password = proxy_parts[3]

            print(f"\n[Запрос {req_num + 1}/{total_requests}] Прокси: {proxy_server}")

            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )

                context = await browser.new_context(
                    proxy={
                        "server": proxy_server,
                        "username": proxy_username,
                        "password": proxy_password,
                    },
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                # Загружаем страницу
                await page.goto("https://www.che168.com/beijing/", wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(4)

                # Проверяем IP (через JS)
                try:
                    ip_info = await page.evaluate("""
                        async () => {
                            try {
                                const resp = await fetch('https://api.ipify.org?format=json', {mode: 'no-cors'});
                                return 'checked';
                            } catch(e) {
                                return 'unknown';
                            }
                        }
                    """)
                    print(f"  IP: проверен")
                except:
                    print(f"  IP: не удалось проверить")

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
                        return cars.slice(0, 5);
                    }
                """)

                await context.close()
                await browser.close()

                # Обрабатываем найденные авто
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

                    if price_cny > 0 and len(all_cars) < 30:
                        all_cars.append({
                            "title_ru": translate(text[:120]),
                            "price_cny": price_cny,
                            "price_rub": round(price_cny * 13, 2),
                            "mileage_km": mileage,
                            "year": year,
                            "image": item['img'],
                            "url": item['link'],
                            "proxy": proxy_server,
                        })

                print(f"  Найдено авто в сессии: {len(car_data)}")
                print(f"  Всего собрано: {len(all_cars)}/30")

            except Exception as e:
                print(f"  ОШИБКА: {str(e)[:100]}")
                try:
                    await browser.close()
                except:
                    pass

            # Переключаемся на следующий прокси
            proxy_index = (proxy_index + 1) % len(PROXIES)

            # Ждем 1 минуту перед следующим запросом (если это не последний)
            if req_num < total_requests - 1:
                print(f"  Ожидание 60 секунд...")
                await asyncio.sleep(60)

    # Фильтруем дубликаты и оставляем 30
    seen = set()
    unique_cars = []
    for car in all_cars:
        key = f"{car['price_cny']}_{car['mileage_km']}_{car['year']}"
        if key not in seen and len(unique_cars) < 30:
            seen.add(key)
            unique_cars.append(car)

    print("\n" + "=" * 60)
    print(f"ИТОГО: {len(unique_cars)} уникальных автомобилей")
    print("=" * 60)

    # Вывод результатов
    for i, car in enumerate(unique_cars[:10]):
        title_preview = car['title_ru'][:60].encode('cp1251', errors='replace').decode('cp1251')
        print(f"[{i+1}] {title_preview}... - {car['price_rub']:,.0f} ₽")

    # Сохраняем JSON
    output_json = Path(__file__).parent / "che168_30_cars.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source": "che168.com",
            "total": len(unique_cars),
            "proxies_used": PROXIES,
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
        .proxy {{ font-size: 12px; color: #999; margin-top: 10px; }}
    </style>
</head>
<body>
    <h1>🚗 Автомобили из Китая (che168.com)</h1>
    <div class="info">
        <div><strong>Дата парсинга:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</div>
        <div><strong>Всего авто:</strong> {len(unique_cars)} шт</div>
        <div><strong>Прокси:</strong> {len(PROXIES)} шт (ротация)</div>
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
                    <div>📅 Год: {c['year']}</div>
                    <div>📊 Пробег: {c['mileage_km']:,.0f} км</div>
                    <div>💰 Цена в Китае: {c['price_cny']:,.0f} CNY</div>
                </div>
                <div class="proxy">Proxy: {c['proxy']}</div>
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

    return unique_cars

if __name__ == "__main__":
    asyncio.run(parse_with_proxy_rotation())
