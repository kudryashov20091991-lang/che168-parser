"""
Использует ТВОЙ уже открытый Chrome с твоей сессией Beget
"""

import asyncio
import subprocess
import os
from playwright.async_api import async_playwright

BEGET_LOGIN = 'ahilesor'
BEGET_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

with open(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php', 'r', encoding='utf-8') as f:
    php_content = f.read()

print(f"PHP файл: {len(php_content)} байт")
print("=" * 60)
print("ИСПОЛЬЗУЮ ТВОЙ CHROME (где ты авторизован)")
print("=" * 60)

# Путь к профилю Chrome пользователя
chrome_data_dir = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
print(f"\nПрофиль Chrome: {chrome_data_dir}")

async def upload():
    async with async_playwright() as p:
        # Запуск с профилем пользователя
        print("\n[1] Запуск твоего Chrome...")
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=chrome_data_dir,
            headless=False,
            args=['--start-maximized', '--disable-notifications'],
            viewport={'width': 1920, 'height': 1080}
        )

        pages = browser.pages
        page = pages[0] if pages else await browser.new_page()

        # Переход на Beget
        print("[2] Переход на cp.beget.com...")
        await page.goto('https://cp.beget.com/', wait_until='networkidle', timeout=120000)
        await page.wait_for_timeout(10000)

        print(f"    URL: {page.url}")
        print(f"    Заголовок: {await page.title()}")

        # Проверка авторизации
        if 'login' in page.url.lower():
            print("\n    Не авторизован, ввожу данные...")

            # Ждем появления полей
            try:
                await page.wait_for_selector('input[name="login"]', timeout=30000)

                # Заполняем
                await page.fill('input[name="login"]', BEGET_LOGIN)
                await page.fill('input[name="passwd"]', BEGET_PASS)
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(15000)

                print(f"    URL после входа: {page.url}")
            except Exception as e:
                print(f"    Ошибка авторизации: {e}")
                print("    Авторизуйся вручную в браузере!")
                await page.wait_for_timeout(30000)
        else:
            print("    Уже авторизован!")

        # Файловый менеджер
        print("\n[3] Файловый менеджер...")
        await page.goto('https://cp.beget.com/filemanager', wait_until='networkidle', timeout=120000)
        await page.wait_for_timeout(10000)

        # public_html
        print("\n[4] public_html...")
        try:
            # Кликаем на public_html
            await page.click('text=public_html', timeout=10000)
            await page.wait_for_timeout(5000)
            print("    Открыта public_html")
        except:
            print("    Клик не сработал, перехожу по URL...")
            await page.goto('https://cp.beget.com/filemanager/public_html', wait_until='networkidle', timeout=120000)
            await page.wait_for_timeout(10000)

        # Создание файла
        print("\n[5] Создание файла che168_parse.php...")
        try:
            # Кнопка "+" или "Создать"
            await page.click('button[title="Создать"], button:has-text("Создать"), .btn-create, span:has-text("+")', timeout=10000)
            await page.wait_for_timeout(2000)

            # Выбрать "Файл"
            await page.click('text=Файл', timeout=5000)
            await page.wait_for_timeout(2000)

            # Имя файла
            await page.fill('input[placeholder*="имя"], input[name="name"]', 'che168_parse.php', timeout=5000)
            await page.click('button:has-text("OK"), button:has-text("Создать")', timeout=5000)
            await page.wait_for_timeout(5000)

            print("    Файл создан!")

        except Exception as e:
            print(f"    Ошибка создания: {e}")

        # Редактирование
        print("\n[6] Редактирование файла...")
        try:
            # Клик по файлу
            await page.click('text=che168_parse.php', timeout=10000)
            await page.wait_for_timeout(3000)

            # Вставка кода
            print("[7] Вставка PHP кода...")

            # Находим textarea и вставляем
            textarea = await page.wait_for_selector('textarea', timeout=10000)
            await textarea.fill(php_content)
            await page.wait_for_timeout(2000)

            # Сохранение
            print("[8] Сохранение...")
            await page.click('button:has-text("Сохранить"), .btn-save', timeout=10000)
            await page.wait_for_timeout(5000)

            print("\n=== УСПЕШНО! ===")
            print("URL: https://ahilesor.beget.ru/che168_parse.php")

        except Exception as e:
            print(f"    Ошибка: {e}")
            print("\n=== СДЕЛАЙ ВРУЧНУЮ ===")
            print("1. Найди che168_parse.php в файловом менеджере")
            print("2. Открой на редактирование")
            print(f"3. Вставь код из che168_beget_final.php")
            print("4. Сохрани")

        print("\nБраузер открыт. Закроется через 30 сек...")
        await page.wait_for_timeout(30000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(upload())
