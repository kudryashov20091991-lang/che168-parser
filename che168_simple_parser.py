"""
Парсер che168.com БЕЗ прокси (для теста)
С использованием Playwright для обхода JS защиты
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Целевые URL
TARGET_URLS = [
    "https://www.che168.com/beijing/",
]

async def parse_page(page, url):
    """Парсит страницу"""
    result = {
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "data": None,
        "error": None,
        "ip": None,
    }

    try:
        # Переходим на страницу
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)  # Ждем загрузки JS

        # Получаем IP
        try:
            ip = await page.evaluate("""
                async () => {
                    try {
                        const resp = await fetch('https://api.ipify.org?format=json');
                        const data = await resp.json();
                        return data.ip;
                    } catch(e) {
                        return 'unknown';
                    }
                }
            """)
            result["ip"] = ip
        except:
            result["ip"] = "unknown"

        # Собираем данные со страницы
        car_data = await page.evaluate("""
            () => {
                const cars = [];

                // Ищем карточки авто
                const selectors = [
                    '[class*="car"]',
                    '[class*="vehicle"]',
                    '.car-list li',
                    '[data-type="car"]',
                    'a[href*="/dealer/"]',
                    'a[href*="/baojia/"]'
                ];

                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach((el, i) => {
                        if (i < 30) {
                            const text = el.innerText || '';
                            const link = el.querySelector('a')?.href || '';
                            const img = el.querySelector('img')?.src || '';

                            // Фильтруем - ищем похожие на авто
                            if (text.length > 30 && (text.includes('万') || text.includes('公里') || text.includes('年'))) {
                                cars.push({
                                    title: text.substring(0, 200).replace(/\s+/g, ' ').trim(),
                                    url: link,
                                    image: img,
                                    raw: text.substring(0, 500).replace(/\s+/g, ' ').trim()
                                });
                            }
                        }
                    });
                    if (cars.length >= 15) break;
                }

                return {
                    cars: cars.slice(0, 15),
                    title: document.title,
                    total_found: cars.length
                };
            }
        """)

        result["data"] = car_data
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)

    return result

async def main():
    """Парсинг 15 лотов"""
    print("=" * 60)
    print("ПАРСИНГ CHE168.COM (БЕЗ ПРОКСИ - ТЕСТ)")
    print("=" * 60)

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = await context.new_page()

        # Парсим
        for url in TARGET_URLS:
            print(f"\nПарсинг: {url}")
            result = await parse_page(page, url)
            results.append(result)

            if result["success"]:
                print(f"IP: {result['ip']}")
                if result["data"]:
                    cars = result["data"].get("cars", [])
                    print(f"Найдено авто: {len(cars)}")

                    # Показываем первые 5
                    for i, car in enumerate(cars[:5]):
                        title = car['title'][:100].encode('cp1251', errors='replace').decode('cp1251')
                        print(f"\n  [{i+1}] {title}...")
                        if car.get('url'):
                            print(f"      URL: {car['url'][:80]}")
            else:
                print(f"Ошибка: {result['error']}")

        await browser.close()

    # Сохраняем результаты
    output_file = Path(__file__).parent / "che168_test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[ИТОГ] Результаты сохранены в: {output_file}")

    # Сохраняем найденные URL авто для дальнейшего парсинга
    all_car_urls = []
    for r in results:
        if r["success"] and r["data"] and r["data"].get("cars"):
            for car in r["data"]["cars"]:
                if car.get("url") and car["url"].startswith("http"):
                    all_car_urls.append(car["url"])

    if all_car_urls:
        urls_file = Path(__file__).parent / "che168_car_urls.txt"
        with open(urls_file, "w", encoding="utf-8") as f:
            for url in all_car_urls[:15]:
                f.write(url + "\n")
        print(f"[ИТОГ] Сохранено {len(all_car_urls)} URL авто в: {urls_file}")

    return results

if __name__ == "__main__":
    asyncio.run(main())
