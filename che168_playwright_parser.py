"""
Парсер che168.com с использованием Playwright и ротацией прокси
Каждый запрос идет через новый прокси
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Прокси для ротации (формат: host:port:username:password)
PROXIES = [
    {"host": "45.32.56.105", "port": "13853", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"host": "45.32.56.105", "port": "13852", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"host": "45.32.56.105", "port": "13851", "username": "Ek0G8F", "password": "GR0Fhj"},
]

# Целевые URL - страницы с автомобилями
# Для теста используем страницу списка авто в Пекине
TARGET_URLS = [
    "https://www.che168.com/beijing/",
]

def get_proxy_server(proxy_info):
    """Формирует строку прокси для Playwright"""
    return f"http://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"

async def parse_with_proxy(page, url, proxy_info):
    """Парсит страницу через указанный прокси"""
    result = {
        "url": url,
        "proxy": f"{proxy_info['host']}:{proxy_info['port']}",
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "data": None,
        "error": None,
        "ip": None,
    }

    try:
        # Переходим на страницу
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)  # Ждем загрузки JS

        # Получаем IP (через JS)
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

                // Ищем карточки авто (разные селекторы)
                const selectors = [
                    '[class*="car-item"]',
                    '[class*="car-card"]',
                    '[class*="vehicle"]',
                    '.car-list li',
                    '[data-type="car"]'
                ];

                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach((el, i) => {
                        if (i < 20) {  // Макс 20 авто со страницы
                            const text = el.innerText || '';
                            const link = el.querySelector('a')?.href || '';

                            if (text.length > 20) {
                                cars.push({
                                    title: text.substring(0, 200),
                                    url: link,
                                    raw: text.substring(0, 500)
                                });
                            }
                        }
                    });
                    if (cars.length > 0) break;
                }

                // Если не нашли, пробуем извлечь из title/body
                if (cars.length === 0) {
                    cars.push({
                        title: document.title,
                        url: location.href,
                        body_preview: document.body.innerText.substring(0, 1000)
                    });
                }

                return { cars };
            }
        """)

        result["data"] = car_data
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)

    return result

async def main():
    """Тестовый парсинг с ротацией прокси"""
    print("=" * 60)
    print("ПАРСИНГ CHE168.COM С PLAYWRIGHT И РОТАЦИЕЙ ПРОКСИ")
    print("=" * 60)

    results = []
    proxy_index = 0

    async with async_playwright() as p:
        # Будем делать 15 запросов (по 5 с каждого прокси)
        total_requests = 15

        for i in range(total_requests):
            proxy = PROXIES[proxy_index % len(PROXIES)]
            proxy_index += 1

            print(f"\n[{i+1}/{total_requests}] Прокси: {proxy['host']}:{proxy['port']}")

            try:
                # Запускаем браузер с прокси
                browser = await p.chromium.launch(
                    proxy={"server": get_proxy_server(proxy)},
                    headless=True,
                )

                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )

                page = await context.new_page()

                # Парсим
                for url in TARGET_URLS:
                    result = await parse_with_proxy(page, url, proxy)
                    results.append(result)

                    if result["success"]:
                        print(f"       IP: {result['ip']}")
                        if result["data"] and result["data"].get("cars"):
                            car_count = len(result["data"]["cars"])
                            print(f"       Найдено авто: {car_count}")
                            # Показываем первый найденный авто
                            first_car = result["data"]["cars"][0]
                            title_preview = first_car.get("title", "N/A")[:80]
                            print(f"       Первый: {title_preview}...")
                    else:
                        print(f"       Ошибка: {result['error'][:100]}")

                await browser.close()

            except Exception as e:
                print(f"       Критическая ошибка: {e}")
                results.append({
                    "url": TARGET_URLS[0] if TARGET_URLS else "",
                    "proxy": f"{proxy['host']}:{proxy['port']}",
                    "success": False,
                    "error": str(e),
                })

            # Ждем 3 минуты перед следующим запросом (для теста 10 сек)
            if i < total_requests - 1:
                wait_time = 10  # Для теста. В продакшене: 180 (3 минуты)
                print(f"       Ожидание {wait_time} сек...")
                await asyncio.sleep(wait_time)

    # Сохраняем результаты
    output_file = Path(__file__).parent / "che168_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[ИТОГ] Результаты сохранены в: {output_file}")

    # Статистика
    success_count = sum(1 for r in results if r["success"])
    print(f"[ИТОГ] Успешных: {success_count}/{len(results)}")

    return results

if __name__ == "__main__":
    asyncio.run(main())
