"""
Загрузка на Beget через Playwright (Chrome)
"""

import asyncio
from playwright.async_api import async_playwright

BEGET_LOGIN = 'ahilesor'
BEGET_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

with open(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php', 'r', encoding='utf-8') as f:
    php_content = f.read()

print(f"PHP файл: {len(php_content)} байт")
print("=" * 60)

async def upload():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--start-maximized'])
        context = await browser.new_context()
        page = await context.new_page()

        print("[1] Авторизация на Beget...")
        await page.goto('https://cp.beget.com/login')
        await page.wait_for_timeout(3000)

        # Ввод логина
        await page.fill('input[name="login"]', BEGET_LOGIN)
        await page.fill('input[name="passwd"]', BEGET_PASS)

        print("[2] Нажатие кнопки входа...")
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(5000)

        print("[3] Переход в Файловый менеджер...")
        await page.goto('https://cp.beget.com/filemanager')
        await page.wait_for_timeout(4000)

        # Переход в public_html
        print("[4] Открытие public_html...")
        try:
            await page.click('[data-name="public_html"]')
            await page.wait_for_timeout(2000)
        except:
            print("    Клик не сработал, пробую URL...")
            await page.goto('https://cp.beget.com/filemanager/public_html')
            await page.wait_for_timeout(3000)

        print("[5] Создание файла...")
        try:
            # Кнопка создать
            await page.click('button[title="Создать"], .btn-create')
            await page.wait_for_timeout(1000)

            # Выбрать "Файл"
            await page.click('text=Файл')
            await page.wait_for_timeout(2000)

            # Имя файла
            await page.fill('input[placeholder*="имя"], input[name="name"]', 'che168_parse.php')
            await page.click('button:has-text("OK"), button:has-text("Создать")')
            await page.wait_for_timeout(3000)

            print("[6] Открытие файла на редактирование...")
            await page.click('text=che168_parse.php')
            await page.wait_for_timeout(2000)

            # Редактор кода
            print("[7] Вставка кода...")
            # Сохраняем контент в переменную для передачи в evaluate
            js_code = """
                () => {
                    const editor = document.querySelector('.CodeMirror') || document.querySelector('textarea');
                    if (editor) {
                        editor.value = arguments[0];
                        editor.dispatchEvent(new Event('input'));
                    }
                }
            """
            await page.evaluate(js_code, php_content)
            await page.wait_for_timeout(2000)

            # Сохранение
            print("[8] Сохранение...")
            await page.click('button:has-text("Сохранить"), .btn-save')
            await page.wait_for_timeout(3000)

            print("\n=== УСПЕШНО! ===")
            print("Файл загружен!")
            print("Открой: https://ahilesor.beget.ru/che168_parse.php")

        except Exception as e:
            print(f"\nОШИБКА: {e}")
            print("\nБраузер открыт — загрузи файл вручную через файловый менеджер")

        print("\nБраузер открыт. Закрою через 30 сек...")
        await page.wait_for_timeout(30000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(upload())
