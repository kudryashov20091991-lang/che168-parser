"""
Полная автоматическая загрузка на Beget
Открывает Chrome, авторизуется, загружает файл
"""

import asyncio
import subprocess
import time
from pathlib import Path
from playwright.async_api import async_playwright

BEGET_LOGIN = 'ahilesor'
BEGET_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

php_path = Path(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php')
php_content = php_path.read_text(encoding='utf-8')

print(f"PHP файл: {len(php_content)} байт")
print("=" * 60)
print("АВТОМАТИЧЕСКАЯ ЗАГРУЗКА НА BEGET")
print("=" * 60)

async def upload():
    async with async_playwright() as p:
        # Запуск Chrome
        print("\n[1] Запуск Chrome...")
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized', '--disable-notifications', '--disable-popup-blocking']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()

        # Авторизация
        print("[2] Авторизация на Beget...")
        await page.goto('https://cp.beget.com/', timeout=60000)
        await page.wait_for_timeout(5000)

        # Если на странице логина
        current_url = page.url
        if 'login' in current_url.lower() or 'auth' in current_url.lower():
            print("    Страница входа, ввожу данные...")
            try:
                await page.wait_for_selector('input[name="login"]', timeout=10000)
                await page.fill('input[name="login"]', BEGET_LOGIN)
                await page.fill('input[name="passwd"]', BEGET_PASS)
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(8000)
                print(f"    URL после входа: {page.url}")
            except Exception as e:
                print(f"    Ошибка ввода: {e}")

        # Файловый менеджер
        print("[3] Переход в Файловый менеджер...")
        await page.goto('https://cp.beget.com/filemanager', timeout=60000)
        await page.wait_for_timeout(5000)

        # public_html
        print("[4] Открытие public_html...")
        try:
            # Ищем и кликаем на public_html
            await page.click('[data-name="public_html"], .file-manager-row:has-text("public_html")', timeout=10000)
            await page.wait_for_timeout(3000)
            print("    public_html открыта")
        except Exception as e:
            print(f"    Ошибка: {e}")
            await page.goto('https://cp.beget.com/filemanager/public_html', timeout=60000)
            await page.wait_for_timeout(3000)

        # Создание файла
        print("[5] Создание файла che168_parse.php...")
        try:
            # Кнопка создать
            create_btn = page.locator('button[title="Создать"], button:has-text("Создать"), .btn-create, [data-action="create"]').first
            await create_btn.click(timeout=10000)
            await page.wait_for_timeout(1500)

            # Выбрать "Файл"
            file_menu = page.locator('text=Файл, text="Create file", .menu-item:has-text("Файл")').first
            await file_menu.click(timeout=5000)
            await page.wait_for_timeout(2000)

            # Ввод имени
            name_input = page.locator('input[placeholder*="имя"], input[name="name"], input[type="text"]').first
            await name_input.fill('che168_parse.php', timeout=5000)
            await page.wait_for_timeout(1000)

            # ОК / Создать
            ok_btn = page.locator('button:has-text("OK"), button:has-text("Создать"), .btn-ok').first
            await ok_btn.click(timeout=5000)
            await page.wait_for_timeout(4000)

            print("    Файл создан!")

        except Exception as e:
            print(f"    Ошибка создания: {e}")

        # Открыть файл на редактирование
        print("[6] Редактирование файла...")
        try:
            # Клик по файлу
            await page.click('text=che168_parse.php, [data-name="che168_parse.php"]', timeout=10000)
            await page.wait_for_timeout(3000)

            # Вставка кода через textarea
            print("[7] Вставка PHP кода...")

            # Пробуем найти textarea редактора
            textarea = page.locator('textarea').first
            await textarea.wait_for(timeout=10000)

            # Фокус и очистка
            await textarea.focus()
            await textarea.press('Control+A')
            await textarea.press('Delete')
            await page.wait_for_timeout(500)

            # Вставка по частям (чтобы не было проблем с большими файлами)
            chunk_size = 500
            for i in range(0, len(php_content), chunk_size):
                chunk = php_content[i:i+chunk_size]
                await textarea.fill(chunk if i == 0 else textarea.input_value() + chunk)
                await page.wait_for_timeout(100)

            await page.wait_for_timeout(2000)

            # Сохранение
            print("[8] Сохранение...")
            save_btn = page.locator('button:has-text("Сохранить"), .btn-save, [data-action="save"]').first
            await save_btn.click(timeout=10000)
            await page.wait_for_timeout(5000)

            print("\n=== УСПЕШНО! ===")
            print("Файл загружен!")
            print("URL: https://ahilesor.beget.ru/che168_parse.php")

        except Exception as e:
            print(f"    Ошибка редактирования: {e}")
            print("\nБраузер открыт — загрузи файл вручную")

        print("\nБраузер открыт. Закроется через 20 сек...")
        await page.wait_for_timeout(20000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(upload())
