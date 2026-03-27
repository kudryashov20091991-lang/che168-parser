"""
che168.com - финальная попытка через прокси
Без проверки IP, сразу парсинг
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

PROXIES = [
    {"server": "http://45.32.56.105:13851", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "http://45.32.56.105:13852", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "http://45.32.56.105:13853", "username": "Ek0G8F", "password": "GR0Fhj"},
]

async def parse():
    print("=" * 60)
    print("CHE168.COM - ПАРСИНГ ЧЕРЕЗ ПРОКСИ")
    print("=" * 60)

    cars = []

    async with async_playwright() as p:
        for i, proxy in enumerate(PROXIES * 5):  # 15 попыток
            if len(cars) >= 10:
                break

            print(f"\n[{i+1}] {proxy['server']}")

            try:
                # Короткий таймаут launch
                browser = await p.chromium.launch(
                    proxy=proxy,
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox'],
                    timeout=10000
                )

                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                # Быстрая загрузка
                await page.goto("https://www.che168.com/beijing/", wait_until="commit", timeout=20000)
                await asyncio.sleep(3)

                # Сбор данных
                data = await page.evaluate("""() => {
                    const cars = [];
                    document.querySelectorAll('*').forEach(el => {
                        const t = el.innerText || '';
                        if (t.length > 50 && t.includes('万') && t.includes('年')) {
                            cars.push({t: t.slice(0, 200), i: el.querySelector('img')?.src || '', l: el.querySelector('a')?.href || ''});
                        }
                    });
                    return cars.slice(0, 15);
                }""")

                await context.close()
                await browser.close()

                print(f"  Найдено: {len(data)}")

                for item in data:
                    if len(cars) >= 10:
                        break
                    t = item['t']
                    price_m = re.search(r'(\d+\.?\d*)\s*万', t)
                    if price_m:
                        price = float(price_m.group(1)) * 10000
                        cars.append({"text": t[:100], "price": price, "proxy": proxy['server']})
                        print(f"  Авто: {price} CNY")

            except Exception as e:
                print(f"  Ошибка: {str(e)[:80]}")
                try: await browser.close()
                except: pass

            await asyncio.sleep(1)

    print(f"\nИтого: {len(cars)} авто")
    return cars

if __name__ == "__main__":
    asyncio.run(parse())
