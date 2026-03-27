"""
Последняя попытка - используем правильный User-Agent и ждем дольше
"""

import asyncio
from playwright.async_api import async_playwright

BEGET_LOGIN = 'ahilesor'
BEGET_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

with open(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php', 'r', encoding='utf-8') as f:
    php_content = f.read()

print(f"PHP: {len(php_content)} байт")
print("=" * 60)

async def upload():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--start-maximized',
                '--disable-notifications',
                '--disable-blink-features=AutomationControlled'
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )

        # Скрываем признаки автоматизации
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        page = await context.new_page()

        print("\n[1] Загрузка Beget...")
        await page.goto('https://cp.beget.com/', timeout=120000)
        await page.wait_for_timeout(15000)

        print(f"    URL: {page.url}")

        # Сохраняем HTML для отладки
        html = await page.content()
        print(f"    HTML размер: {len(html)} байт")

        # 2. Авторизация
        print("\n[2] Авторизация...")

        # Ищем все input на странице
        inputs = await page.query_selector_all('input')
        print(f"    Найдено input: {len(inputs)}")

        for i, inp in enumerate(inputs):
            name = await inp.get_attribute('name')
            placeholder = await inp.get_attribute('placeholder')
            print(f"      [{i}] name={name}, placeholder={placeholder}")

        # Пробуем заполнить логин
        try:
            login_field = await page.wait_for_selector('input[name="login"]', timeout=30000)
            print("    Поле login найдено!")

            await login_field.fill(BEGET_LOGIN)
            print("    Ввел логин")

            pass_field = await page.query_selector('input[name="passwd"]')
            if pass_field:
                await pass_field.fill(BEGET_PASS)
                print("    Ввел пароль")

                submit = await page.query_selector('button[type="submit"]')
                if submit:
                    await submit.click()
                    print("    Нажал Submit")
                    await page.wait_for_timeout(15000)
                    print(f"    URL: {page.url}")
            else:
                print("    Поле passwd не найдено")

        except Exception as e:
            print(f"    Ошибка: {e}")

        # 3. Файловый менеджер
        print("\n[3] Переход в файловый менеджер...")
        await page.goto('https://cp.beget.com/filemanager', timeout=120000)
        await page.wait_for_timeout(15000)

        # Скриншот
        await page.screenshot(path='debug_fm.png')
        print("    Скриншот: debug_fm.png")

        # 4. public_html
        print("\n[4] public_html...")
        try:
            # Ищем по тексту
            elements = await page.query_selector_all('text=public_html')
            print(f"    Найдено элементов 'public_html': {len(elements)}")

            if elements:
                await elements[0].click()
                await page.wait_for_timeout(5000)
                print("    Клик успешен")
            else:
                print("    Не найдено, перехожу по URL")
                await page.goto('https://cp.beget.com/filemanager/public_html', timeout=120000)
                await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"    Ошибка: {e}")

        print("\n=== БРАУЗЕР ОТКРЫТ ===")
        print("Сделай загрузку вручную через файловый менеджер")
        print(f"Файл готов: che168_beget_final.php ({len(php_content)} байт)")

        await page.wait_for_timeout(60000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(upload())
