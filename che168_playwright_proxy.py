#!/usr/bin/env python3
"""
Парсер che168.com через Playwright с прокси
"""

from playwright.sync_api import sync_playwright
import json
import time

PROXIES = [
    {'server': 'http://45.32.56.105:13851', 'username': 'Ek0G8F', 'password': 'GR0Fhj'},
    {'server': 'http://45.32.56.105:13852', 'username': 'Ek0G8F', 'password': 'GR0Fhj'},
    {'server': 'http://45.32.56.105:13853', 'username': 'Ek0G8F', 'password': 'GR0Fhj'},
]

cars = []
results = []

print("=" * 60)
print("ПАРСИНГ CHE168.COM ЧЕРЕЗ PLAYWRIGHT + ПРОКСИ")
print("=" * 60)

with sync_playwright() as p:
    for i, proxy in enumerate(PROXIES):
        if len(cars) >= 10:
            break

        proxy_label = proxy['server'].split('//')[1]
        print(f"\n[Попытка {i+1}] Прокси: {proxy_label}")

        try:
            browser = p.chromium.launch(
                proxy=proxy,
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
            )

            page = context.new_page()

            # Запрос страницы
            page.set_default_timeout(40000)
            page.goto('https://www.che168.com/beijing/', wait_until='domcontentloaded')

            # Проверка IP
            ip_page = context.new_page()
            ip_page.set_default_timeout(15000)
            try:
                ip_page.goto('https://api.ipify.org/', wait_until='domcontentloaded')
                ip_text = ip_page.inner_text('body')
                print(f"  IP прокси: {ip_text}")
            except:
                print("  IP: не определен")
            finally:
                ip_page.close()

            # Получаем HTML
            html = page.content()
            print(f"  Размер HTML: {len(html)} байт")

            # Парсинг цен
            import re
            prices = re.findall(r'(\d+\.?\d*)\s*万', html)
            for price in prices:
                price_cny = float(price) * 10000
                if price_cny > 50000 and len(cars) < 10:
                    cars.append({
                        'price_cny': price_cny,
                        'price_rub': round(price_cny * 13, 2),
                        'proxy': proxy_label,
                    })
                    print(f"  [AUTO] {price_cny:,.0f} CNY (~{price_cny * 13:,.0f} RUB)")

            results.append({'proxy': proxy_label, 'status': 'ok', 'size': len(html)})
            browser.close()

        except Exception as e:
            print(f"  [ERR] {str(e)[:200]}")
            results.append({'proxy': proxy_label, 'status': 'error', 'error': str(e)[:100]})
            try:
                browser.close()
            except:
                pass

        time.sleep(1)

print("\n" + "=" * 60)
print(f"ИТОГО: {len(cars)} автомобилей")
print("=" * 60)

output = {
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'source': 'che168.com',
    'proxies_tested': len(results),
    'cars_found': len(cars),
    'results': results,
    'cars': cars,
}

with open('che168_result.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nСохранено: che168_result.json")
print(f"\nРезультаты по прокси:")
for r in results:
    print(f"  {r['proxy']}: {r['status']}")

print(f"\nАвтомобили ({len(cars)}):")
for car in cars:
    print(f"  {car['price_cny']:,.0f} CNY = {car['price_rub']:,.0f} RUB")
