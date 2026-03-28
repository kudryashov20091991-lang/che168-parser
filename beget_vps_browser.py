#!/usr/bin/env python3
"""
Получение данных VPS через браузер (Playwright)
"""

from playwright.sync_api import sync_playwright
import time
import re

BEGET_LOGIN = 'ahilesor'
BEGET_PASSWORD = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

print("=" * 60)
print("ПОЛУЧЕНИЕ ДАННЫХ VPS ЧЕРЕЗ БРАУЗЕР")
print("=" * 60)

with sync_playwright() as p:
    # Запуск браузера
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()

    # Логин
    print("\n[1] Логин на Beget...")
    page.goto('https://cp.beget.com/login', timeout=60000)
    page.wait_for_selector('input[name="login"]', timeout=30000)

    page.fill('input[name="login"]', BEGET_LOGIN)
    page.fill('input[name="password"]', BEGET_PASSWORD)
    page.click('button[type="submit"]')

    # Ожидание перехода на панель
    page.wait_for_url('https://cp.beget.com/**', timeout=30000)
    print("    Успешно!")

    # Переход на VPS
    print("\n[2] Переход в раздел VPS...")
    page.goto('https://cp.beget.com/vps', timeout=60000)
    time.sleep(3)

    # Получаем HTML
    html = page.content()

    # Ищем IP адреса
    ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', html)
    if ips:
        print(f"\n[3] Найдены IP: {set(ips)}")

    # Ищем домен VPS
    vps_domains = re.findall(r'[a-z0-9]+\.vps\.beget\.com', html, re.IGNORECASE)
    if vps_domains:
        print(f"    VPS домены: {set(vps_domains)}")

    # Сохраняем HTML
    with open('vps_browser.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\nHTML сохранен в vps_browser.html")

    browser.close()

print("\n" + "=" * 60)
print("ГОТОВО")
print("=" * 60)
