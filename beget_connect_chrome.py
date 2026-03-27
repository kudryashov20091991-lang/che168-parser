"""
Подключение к УЖЕ ОТКРЫТОМУ Chrome и загрузка на Beget
"""

import asyncio
import json
from playwright.async_api import async_playwright

BEGET_LOGIN = 'ahilesor'
BEGET_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

with open(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php', 'r', encoding='utf-8') as f:
    php_content = f.read()

print(f"PHP файл: {len(php_content)} байт")
print("=" * 60)
print("ПОДКЛЮЧЕНИЕ К ОТКРЫТОМУ CHROME")
print("=" * 60)

async def upload():
    # Подключаемся к запущенному Chrome через CDP
    # Chrome должен быть запущен с флагом --remote-debugging-port=9222

    print("\n[1] Подключение к Chrome...")

    try:
        async with async_playwright() as p:
            # Подключение к существующему браузеру
            browser = await p.chromium.connect_over_cdp(
                endpoint_url="http://localhost:9222",
                timeout=30000
            )

            print("    УСПЕШНО подключено!")
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = context.pages[0] if context.pages else await context.new_page()

            # Переход на Beget
            print("[2] Переход на cp.beget.com...")
            await page.goto('https://cp.beget.com/', wait_until='networkidle', timeout=60000)
            print(f"    URL: {page.url}")

            # Проверка авторизации
            if 'login' in page.url.lower():
                print("[3] Ввод логина/пароля...")
                await page.fill('input[name="login"]', BEGET_LOGIN)
                await page.fill('input[name="passwd"]', BEGET_PASS)
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(5000)
            else:
                print("    Уже авторизован!")

            # Файловый менеджер
            print("[4] Файловый менеджер...")
            await page.goto('https://cp.beget.com/filemanager', wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(3000)

            # public_html
            print("[5] Переход в public_html...")
            try:
                await page.click('[data-name="public_html"]')
                await page.wait_for_timeout(2000)
            except:
                await page.goto('https://cp.beget.com/filemanager/public_html', wait_until='networkidle')
                await page.wait_for_timeout(3000)

            # Создание файла
            print("[6] Создание che168_parse.php...")
            try:
                # Кнопка создать
                await page.click('button:has-text("Создать"), button:has-text("+"), .btn-create', timeout=10000)
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
                print(f"    Ошибка: {e}")

            # Редактирование
            print("[7] Редактирование файла...")
            try:
                await page.click('text=che168_parse.php', timeout=5000)
                await page.wait_for_timeout(2000)

                # Вставка кода
                print("[8] Вставка PHP кода...")
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
                print("[9] Сохранение...")
                await page.click('button:has-text("Сохранить"), .btn-save', timeout=5000)
                await page.wait_for_timeout(3000)

                print("\n=== УСПЕШНО! ===")
                print("URL: https://ahilesor.beget.ru/che168_parse.php")

            except Exception as e:
                print(f"    Ошибка: {e}")
                print("\nБраузер открыт — загрузи вручную")

            print("\nГотово!")
            await browser.close()

    except Exception as e:
        print(f"\nОШИБКА подключения: {e}")
        print("\nЗапусти Chrome с флагом --remote-debugging-port=9222")
        print("Или закрой Chrome и запусти этот скрипт — он откроет Chrome сам")

if __name__ == "__main__":
    asyncio.run(upload())
