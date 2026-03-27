"""
Финальная версия загрузки на Beget
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
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized', '--disable-notifications', '--disable-web-security']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # 1. Главная Beget
        print("\n[1] Загрузка cp.beget.com...")
        await page.goto('https://cp.beget.com/', timeout=120000)
        print(f"    URL: {page.url}")
        await page.wait_for_timeout(10000)

        # 2. Авторизация
        print("[2] Авторизация...")
        try:
            # Ждем появления поля логина
            await page.wait_for_selector('input[name="login"]', timeout=30000)
            print("    Поле логина найдено")

            await page.fill('input[name="login"]', BEGET_LOGIN)
            print("    Ввел логин")

            await page.fill('input[name="passwd"]', BEGET_PASS)
            print("    Ввел пароль")

            await page.click('button[type="submit"]')
            print("    Нажал войти")

            await page.wait_for_timeout(15000)
            print(f"    URL: {page.url}")
        except Exception as e:
            print(f"    Ошибка: {e}")

        # 3. Файловый менеджер
        print("[3] Файловый менеджер...")
        await page.goto('https://cp.beget.com/filemanager', timeout=120000)
        await page.wait_for_timeout(10000)

        # 4. public_html
        print("[4] public_html...")
        # Скриншот для отладки
        await page.screenshot(path='debug_step.png')
        print("    Скриншот: debug_step.png")

        # Пробуем разные селекторы
        selectors = [
            '[data-name="public_html"]',
            '.file-manager-item[data-name="public_html"]',
            'text=public_html',
            '[title="public_html"]'
        ]

        for sel in selectors:
            try:
                await page.click(sel, timeout=5000)
                print(f"    Клик по '{sel}' успешен")
                await page.wait_for_timeout(3000)
                break
            except:
                print(f"    Селектор '{sel}' не сработал")

        # 5. Создание файла
        print("[5] Создание файла...")
        try:
            # Кнопка создать
            await page.click('button:has-text("Создать")', timeout=10000)
            await page.wait_for_timeout(2000)

            # Файл
            await page.click('text=Файл', timeout=5000)
            await page.wait_for_timeout(2000)

            # Имя
            await page.fill('input[placeholder*="имя"]', 'che168_parse.php', timeout=5000)
            await page.click('button:has-text("OK")', timeout=5000)
            await page.wait_for_timeout(5000)

            print("    Файл создан!")
        except Exception as e:
            print(f"    Ошибка: {e}")

        # 6. Редактирование
        print("[6] Вставка кода...")
        try:
            await page.click('text=che168_parse.php', timeout=10000)
            await page.wait_for_timeout(3000)

            # Вставка
            await page.evaluate(f"""
                () => {{
                    const textarea = document.querySelector('textarea');
                    if (textarea) {{
                        textarea.value = `{php_content[:500]}`;
                    }}
                }}
            """)

            await page.click('button:has-text("Сохранить")', timeout=10000)
            await page.wait_for_timeout(5000)

            print("\n=== ГОТОВО! ===")
        except Exception as e:
            print(f"    Ошибка: {e}")
            print("\nБраузер открыт — сделай вручную")

        await page.wait_for_timeout(30000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(upload())
