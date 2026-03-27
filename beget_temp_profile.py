"""
Загрузка на Beget через временный профиль Chrome
"""

import asyncio
from playwright.async_api import async_playwright

BEGET_LOGIN = 'ahilesor'
BEGET_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

with open(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php', 'r', encoding='utf-8') as f:
    php_content = f.read()

print(f"PHP файл: {len(php_content)} байт")
print("=" * 60)
print("ЗАГРУЗКА НА BEGET")
print("=" * 60)

async def upload():
    async with async_playwright() as p:
        # Запуск с временным профилем
        print("\n[1] Запуск Chrome...")
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized', '--disable-notifications']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # 2. Авторизация
        print("[2] Переход на Beget...")
        await page.goto('https://cp.beget.com/', timeout=120000)
        await page.wait_for_timeout(10000)

        print(f"    URL: {page.url}")

        # 3. Авторизация
        print("[3] Авторизация...")
        try:
            await page.wait_for_selector('input[name="login"]', timeout=30000)
            await page.fill('input[name="login"]', BEGET_LOGIN)
            await page.fill('input[name="passwd"]', BEGET_PASS)
            await page.click('button[type="submit"]')
            print("    Ввел данные, жду...")
            await page.wait_for_timeout(15000)
            print(f"    URL: {page.url}")
        except Exception as e:
            print(f"    Ошибка: {e}")
            print("    Авторизуйся вручную!")

        # 4. Файловый менеджер
        print("\n[4] Файловый менеджер...")
        await page.goto('https://cp.beget.com/filemanager', timeout=120000)
        await page.wait_for_timeout(10000)

        # 5. public_html
        print("[5] public_html...")
        try:
            await page.click('text=public_html', timeout=10000)
            await page.wait_for_timeout(5000)
        except:
            await page.goto('https://cp.beget.com/filemanager/public_html', timeout=120000)
            await page.wait_for_timeout(10000)

        # 6. Создание файла
        print("\n[6] Создание файла che168_parse.php...")
        try:
            await page.click('button:has-text("Создать"), .btn-create', timeout=10000)
            await page.wait_for_timeout(2000)
            await page.click('text=Файл', timeout=5000)
            await page.wait_for_timeout(2000)
            await page.fill('input[placeholder*="имя"]', 'che168_parse.php', timeout=5000)
            await page.click('button:has-text("OK")', timeout=5000)
            await page.wait_for_timeout(5000)
            print("    Файл создан!")
        except Exception as e:
            print(f"    Ошибка: {e}")

        # 7. Редактирование
        print("\n[7] Редактирование...")
        print("    Браузер открыт — загрузи файл вручную")
        print(f"    Файл: che168_beget_final.php ({len(php_content)} байт)")

        await page.wait_for_timeout(120000)  # 2 минуты на загрузку
        await browser.close()

if __name__ == "__main__":
    asyncio.run(upload())
