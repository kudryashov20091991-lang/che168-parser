"""Проверка прокси - правильный формат для Playwright"""
import asyncio
from playwright.async_api import async_playwright

PROXIES = [
    {"host": "45.32.56.105", "port": "13851", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"host": "45.32.56.105", "port": "13852", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"host": "45.32.56.105", "port": "13853", "username": "Ek0G8F", "password": "GR0Fhj"},
]

def get_proxy_server(proxy_info):
    return f"http://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"

async def check_proxy(proxy_info, index):
    print(f"\n[Прокси {index+1}] {proxy_info['host']}:{proxy_info['port']}")
    proxy_server = get_proxy_server(proxy_info)
    print(f"  Server строка: {proxy_server[:50]}...")

    try:
        async with async_playwright() as p:
            # Запускаем браузер С прокси на уровне launch
            browser = await p.chromium.launch(
                proxy={"server": proxy_server},
                headless=True,
            )

            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
            )

            page = await context.new_page()

            # Проверяем IP
            try:
                await page.goto("https://api.ipify.org?format=json", timeout=20000)
                content = await page.content()
                print(f"  IP ответ: {content[:100]}")
            except Exception as e:
                print(f"  IP check: {str(e)[:80]}")

            # Проверяем che168
            try:
                await page.goto("https://www.che168.com/", timeout=30000, wait_until="domcontentloaded")
                await asyncio.sleep(2)
                title = await page.title()
                print(f"  che168 title: {title[:80]}")
                print(f"  СТАТУС: РАБОТАЕТ")
            except Exception as e:
                print(f"  che168: {str(e)[:80]}")

            await browser.close()

    except Exception as e:
        print(f"  ОШИБКА: {str(e)[:150]}")

async def main():
    print("=" * 60)
    print("ПРОВЕРКА ПРОКСИ - ПРАВИЛЬНЫЙ ФОРМАТ")
    print("=" * 60)

    for i, proxy in enumerate(PROXIES):
        await check_proxy(proxy, i)

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
