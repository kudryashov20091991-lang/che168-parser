"""
Автоматическая загрузка на Beget через Playwright
"""

import asyncio
from playwright.async_api import async_playwright

BEGET_LOGIN = 'ahilesor'
BEGET_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

with open(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php', 'r', encoding='utf-8') as f:
    php_content = f.read()

print(f"PHP файл: {len(php_content)} байт")
print("=" * 60)
print("АВТОМАТИЧЕСКАЯ ЗАГРУЗКА НА BEGET")
print("=" * 60)

async def upload():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()

        # 1. Авторизация
        print("\n[1] Авторизация...")
        await page.goto('https://cp.beget.com/', wait_until='networkidle', timeout=60000)
        print(f"    Текущий URL: {page.url}")

        # Проверяем, не авторизованы ли уже
        if 'login' in page.url.lower():
            print("    Страница входа, ввожу данные...")
            await page.wait_for_selector('input[name="login"]', timeout=10000)
            await page.fill('input[name="login"]', BEGET_LOGIN)
            await page.fill('input[name="passwd"]', BEGET_PASS)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(5000)
            print(f"    URL после входа: {page.url}")

        # 2. Файловый менеджер
        print("\n[2] Файловый менеджер...")
        await page.goto('https://cp.beget.com/filemanager', wait_until='networkidle', timeout=60000)
        await page.wait_for_timeout(3000)

        # 3. public_html
        print("[3] Переход в public_html...")
        try:
            await page.click('[data-name="public_html"], text=public_html')
            await page.wait_for_timeout(2000)
        except:
            print("    Клик не сработал")

        # 4. Создание файла
        print("[4] Создание файла che168_parse.php...")
        try:
            # Кнопка создать
            create_btn = page.locator('button:has-text("Создать"), button:has-text("+"), .btn-create').first
            await create_btn.click(timeout=5000)
            await page.wait_for_timeout(1000)

            # Файл
            await page.click('text=Файл', timeout=5000)
            await page.wait_for_timeout(2000)

            # Имя
            await page.fill('input[placeholder*="имя"], input[name="name"]', 'che168_parse.php', timeout=5000)
            await page.click('button:has-text("OK"), button:has-text("Создать")', timeout=5000)
            await page.wait_for_timeout(3000)

            print("    Файл создан!")

        except Exception as e:
            print(f"    Ошибка создания: {e}")

        # 5. Открыть файл
        print("[5] Редактирование файла...")
        try:
            await page.click('text=che168_parse.php', timeout=5000)
            await page.wait_for_timeout(2000)

            # Вставка кода
            print("[6] Вставка PHP кода...")
            await page.evaluate("""
                (content) => {
                    const editor = document.querySelector('textarea') || document.querySelector('.CodeMirror textarea');
                    if (editor) {
                        editor.value = content;
                        editor.dispatchEvent(new Event('input', { bubbles: true }));
                        editor.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            """, php_content)
            await page.wait_for_timeout(2000)

            # Сохранение
            print("[7] Сохранение...")
            await page.click('button:has-text("Сохранить"), .btn-save', timeout=5000)
            await page.wait_for_timeout(3000)

            print("\n=== УСПЕШНО! ===")
            print("URL: https://ahilesor.beget.ru/che168_parse.php")

        except Exception as e:
            print(f"    Ошибка: {e}")
            print("\n=== ВРУЧНУЮ ===")
            print("1. Найди che168_parse.php в списке")
            print("2. Открой на редактирование")
            print("3. Вставь код из che168_beget_final.php")
            print("4. Сохрани")

        print("\nБраузер открыт (15 сек)...")
        await page.wait_for_timeout(15000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(upload())
