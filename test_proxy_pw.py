"""Проверка прокси через Playwright"""
import asyncio
from playwright.async_api import async_playwright

PROXIES = [
    {"server": "45.32.56.105:13851", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "45.32.56.105:13852", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "45.32.56.105:13853", "username": "Ek0G8F", "password": "GR0Fhj"},
]

async def check_proxy(proxy_info, index):
    print(f"\n[Прокси {index+1}] {proxy_info['server']}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            context = await browser.new_context(
                proxy={
                    "server": f"http://{proxy_info['server']}",
                    "username": proxy_info["username"],
                    "password": proxy_info["password"],
                },
                viewport={"width": 1920, "height": 1080},
            )

            page = await context.new_page()

            # Пробуем проверить IP
            try:
                await page.goto("https://api.ipify.org?format=json", timeout=20000)
                content = await page.content()
                print(f"  Ответ: {content[:200]}")
            except Exception as e:
                print(f"  IP check error: {str(e)[:100]}")

            # Пробуем зайти на che168
            try:
                await page.goto("https://www.che168.com/", timeout=30000, wait_until="domcontentloaded")
                await asyncio.sleep(3)
                title = await page.title()
                print(f"  che168 title: {title[:100]}")
                print(f"  СТАТУС: РАБОТАЕТ")
            except Exception as e:
                print(f"  che168 error: {str(e)[:100]}")

            await browser.close()

    except Exception as e:
        print(f"  ОШИБКА: {str(e)[:150]}")

async def main():
    print("=" * 60)
    print("ПРОВЕРКА ПРОКСИ ЧЕРЕЗ PLAYWRIGHT")
    print("=" * 60)

    for i, proxy in enumerate(PROXIES):
        await check_proxy(proxy, i)

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
