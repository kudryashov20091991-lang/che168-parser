#!/usr/bin/env python3
"""
Автоматическая настройка VPS на Beget
Обход VPN блокировок через веб-интерфейс
"""

from playwright.sync_api import sync_playwright
import time

BEGET_LOGIN = 'ahilesor'
BEGET_PASSWORD = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'
VPS_IP = '185.46.80.165'
VPS_ROOT_PASSWORD = 'BegetVPS2024!'

print("=" * 60)
print("АВТОМАТИЧЕСКАЯ НАСТРОЙКА VPS")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    page = context.new_page()

    # Шаг 1: Логин
    print("\n[1] Логин на Beget...")
    page.goto('https://cp.beget.com/login', timeout=60000)

    try:
        page.fill('input[name="login"]', BEGET_LOGIN)
        page.fill('input[name="password"]', BEGET_PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_url('https://cp.beget.com/**', timeout=30000)
        print("    Успешно!")
    except Exception as e:
        print(f"    Ошибка: {e}")
        # Пробуем альтернативный вход
        page.goto('https://cp.beget.com', timeout=60000)
        time.sleep(5)

    # Шаг 2: Переход в VPS
    print("\n[2] Переход в раздел VPS...")
    page.goto('https://cp.beget.com/vps', timeout=60000)
    time.sleep(3)

    # Шаг 3: Открытие веб-консоли
    print("\n[3] Открытие веб-консоли VPS...")

    # Ищем кнопку консоли
    try:
        # Пробуем разные селекторы
        selectors = [
            'a[href*="console"]',
            'button:has-text("Консоль")',
            'button:has-text("Console")',
            'a:has-text("SSH")',
            '[data-testid="vps-console"]',
        ]

        for selector in selectors:
            try:
                page.click(selector, timeout=5000)
                print(f"    Клик по: {selector}")
                break
            except:
                continue

        time.sleep(5)

        # Сохраняем скриншот для отладки
        page.screenshot(path='vps_console.png')
        print("    Скриншот: vps_console.png")

    except Exception as e:
        print(f"    Ошибка консоли: {e}")

    # Шаг 4: Проверка файлового менеджера
    print("\n[4] Проверка файлового менеджера...")
    page.goto('https://cp.beget.com/filemanager', timeout=60000)
    time.sleep(3)
    page.screenshot(path='filemanager.png')
    print("    Скриншот: filemanager.png")

    browser.close()

print("\n" + "=" * 60)
print("ГОТОВО - проверьте скриншоты")
print("=" * 60)
