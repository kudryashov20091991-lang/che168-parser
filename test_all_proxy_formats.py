"""Тест всех форматов прокси"""
import asyncio
from playwright.async_api import async_playwright

# Прокси данные
HOST = "45.32.56.105"
PORTS = ["13851", "13852", "13853"]
USER = "Ek0G8F"
PASSWD = "GR0Fhj"

async def test_format(format_name, proxy_config):
    print(f"\n[{format_name}]")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                proxy=proxy_config,
                headless=True,
            )
            context = await browser.new_context()
            page = await context.new_page()

            # Быстрый тест
            await page.goto("https://httpbin.org/ip", timeout=15000)
            content = await page.content()
            print(f"  OK: {content[:200]}")
            await browser.close()
            return True
    except Exception as e:
        print(f"  FAIL: {str(e)[:100]}")
        return False

async def main():
    print("=" * 60)
    print("ТЕСТ ФОРМАТОВ ПРОКСИ")
    print("=" * 60)

    formats = [
        ("HTTP auth in URL", {"server": f"http://{USER}:{PASSWD}@{HOST}:{PORTS[0]}"}),
        ("HTTP separate", {"server": f"http://{HOST}:{PORTS[0]}", "username": USER, "password": PASSWD}),
        ("HTTPS auth in URL", {"server": f"https://{USER}:{PASSWD}@{HOST}:{PORTS[0]}"}),
        ("SOCKS5", {"server": f"socks5://{HOST}:{PORTS[0]}"}),
        ("SOCKS5 auth", {"server": f"socks5://{USER}:{PASSWD}@{HOST}:{PORTS[0]}"}),
        ("Direct IP no auth", {"server": f"http://{HOST}:{PORTS[0]}"}),
    ]

    for name, config in formats:
        await test_format(name, config)

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
