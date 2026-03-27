"""
Загрузка на sprutio.beget.com - файловый менеджер
"""

import asyncio
from playwright.async_api import async_playwright

BEGET_LOGIN = 'ahilesor'
BEGET_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

with open(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php', 'r', encoding='utf-8') as f:
    php_content = f.read()

print(f"PHP файл: {len(php_content)} байт")
print("=" * 60)
print("ЗАГРУЗКА НА SPRUTIO.BEGET.COM")
print("=" * 60)

async def upload():
    async with async_playwright() as p:
        print("\n[1] Запуск Chrome...")
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized', '--disable-notifications']
        )

        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        # Переход на sprutio
        print("[2] Переход на https://sprutio.beget.com/...")
        await page.goto('https://sprutio.beget.com/', timeout=120000)
        await page.wait_for_timeout(10000)

        print(f"    URL: {page.url}")
        print(f"    Заголовок: {await page.title()}")

        # Проверка авторизации
        if 'login' in page.url.lower() or 'auth' in page.url.lower():
            print("[3] Авторизация...")
            try:
                await page.wait_for_selector('input[name="login"]', timeout=30000)
                await page.fill('input[name="login"]', BEGET_LOGIN)
                await page.fill('input[name="passwd"]', BEGET_PASS)
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(15000)
                print(f"    URL: {page.url}")
            except Exception as e:
                print(f"    Ошибка: {e}")
                print("    Авторизуйся вручную!")
                await page.wait_for_timeout(30000)
        else:
            print("    Уже авторизован!")

        # Файловый менеджер
        print("\n[4] Переход в файловый менеджер...")
        # Ищем ссылку на файловый менеджер
        try:
            await page.click('text=Файловый менеджер, text=File Manager, a[href*="file"]', timeout=10000)
            await page.wait_for_timeout(5000)
        except:
            print("    Клик не сработал, остаемся на текущей")

        # Создание файла
        print("\n[5] Создание файла che168_parse.php...")
        print("    Браузер открыт — загрузи файл через интерфейс")
        print(f"    Файл для копирования: che168_beget_final.php")
        print(f"    Размер: {len(php_content)} байт")

        # Ждем пока пользователь загрузит файл
        print("\n    Загрузи файл и нажми Enter в консоли...")
        input("Нажми Enter когда файл загружен...")

        print("\n[6] Проверка файла...")
        await page.goto('https://ahilesor.beget.ru/che168_parse.php', timeout=60000)
        await page.wait_for_timeout(5000)
        print(f"    URL: {page.url}")

        content = await page.content()
        if len(content) > 1000:
            print("    Файл работает!")
        else:
            print("    Файл не загрузился")

        await page.wait_for_timeout(30000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(upload())
