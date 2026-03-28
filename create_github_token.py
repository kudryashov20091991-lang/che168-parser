#!/usr/bin/env python3
"""
Автоматическое создание токена GitHub через браузер
"""

from playwright.sync_api import sync_playwright
import time
import re

GITHUB_EMAIL = 'kudryashov20091991@gmail.com'
GITHUB_PASSWORD = '!1Vbkkbfhl _4'

print("=" * 60)
print("СОЗДАНИЕ ТОКЕНА GITHUB")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()

    # Шаг 1: Логин
    print("\n[1] Вход на GitHub...")
    page.goto('https://github.com/login', timeout=60000)

    try:
        page.fill('input#login_field', GITHUB_EMAIL)
        page.fill('input#password', GITHUB_PASSWORD)
        page.click('input[type="submit"]')
        page.wait_for_url('https://github.com/**', timeout=30000)
        print("    Успешно!")
    except Exception as e:
        print(f"    Ошибка входа: {e}")
        browser.close()
        exit(1)

    # Шаг 2: Переход к созданию токена
    print("\n[2] Переход к настройкам токенов...")
    page.goto('https://github.com/settings/tokens', timeout=60000)
    time.sleep(3)

    # Шаг 3: Создание токена (classic)
    print("\n[3] Создание токена...")
    try:
        # Ищем ссылку на создание classic токена
        page.click('a[href*="/settings/tokens/new"]', timeout=10000)
        page.wait_for_url('https://github.com/settings/tokens/new', timeout=30000)
        time.sleep(2)
    except:
        print("    Классическая страница токенов...")
        page.goto('https://github.com/settings/tokens/new', timeout=60000)
        time.sleep(3)

    # Шаг 4: Заполнение формы
    print("\n[4] Заполнение формы...")
    try:
        # Имя токена
        page.fill('input[name="oauth_description"]', 'che168-parser')

        # Срок действия (опционально)
        # page.select_option('select[name="oauth[expires_at]"]', '90')

        # Permissions: repo
        page.check('input#repo', timeout=5000)

        # Permissions: workflow
        page.check('input#workflow', timeout=5000)

        print("    Форма заполнена!")
    except Exception as e:
        print(f"    Ошибка заполнения: {e}")

    # Шаг 5: Генерация токена
    print("\n[5] Генерация токена...")
    try:
        page.click('button[type="submit"]', timeout=10000)

        # Ожидание страницы с токеном
        page.wait_for_selector('input[name="oauth_token"]', timeout=30000)

        # Получение токена
        token_input = page.query_selector('input[name="oauth_token"]')
        token = token_input.input_value()

        print(f"\n    ТОКЕН СОЗДАН: {token[:10]}...")

        # Сохранение токена
        with open('github_token.txt', 'w') as f:
            f.write(token)

        print("\n    Сохранено в: github_token.txt")

    except Exception as e:
        print(f"    Ошибка генерации: {e}")
        token = None

    browser.close()

print("\n" + "=" * 60)
if token:
    print(f"ГОТОВО! Токен: {token}")
else:
    print("Не удалось создать токен автоматически.")
    print("Откройте: https://github.com/settings/tokens/new")
print("=" * 60)
