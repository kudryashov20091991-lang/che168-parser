#!/usr/bin/env python3
"""
Парсер che168.com через прокси
Запуск локально с выводом результата
"""

import requests
import re
import json
import time

PROXIES = [
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13851', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13851'},
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13852', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13852'},
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13853', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13853'},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xhtml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
}

cars = []
results = []

print("=" * 60)
print("ПАРСИНГ CHE168.COM ЧЕРЕЗ ПРОКСИ")
print("=" * 60)

for i, proxy in enumerate(PROXIES):
    if len(cars) >= 10:
        break

    proxy_label = proxy['http'].split('@')[1]
    print(f"\n[Попытка {i+1}] Прокси: {proxy_label}")

    try:
        # Проверка IP
        ip_resp = requests.get('https://api.ipify.org/', proxies=proxy, headers=HEADERS, timeout=15)
        print(f"  IP прокси: {ip_resp.text}")

        # Запрос к сайту
        resp = requests.get('https://www.che168.com/beijing/', proxies=proxy, headers=HEADERS, timeout=30)
        print(f"  HTTP статус: {resp.status_code}")
        print(f"  Размер ответа: {len(resp.text)} байт")

        if resp.status_code == 200 and len(resp.text) > 1000:
            html = resp.text

            # Поиск цен (XXX万)
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

            results.append({'proxy': proxy_label, 'status': 'ok', 'http': resp.status_code, 'size': len(resp.text)})
        else:
            results.append({'proxy': proxy_label, 'status': 'error', 'http': resp.status_code})

    except Exception as e:
        print(f"  [ERR] {e}")
        results.append({'proxy': proxy_label, 'status': 'error', 'error': str(e)})

    time.sleep(1)

print("\n" + "=" * 60)
print(f"ИТОГО: {len(cars)} автомобилей")
print("=" * 60)

# Сохранение результата
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
print(f"\nРезультаты:")
for r in results:
    print(f"  {r['proxy']}: {r['status']}")

print(f"\nАвтомобили ({len(cars)}):")
for car in cars:
    print(f"  {car['price_cny']:,.0f} CNY = {car['price_rub']:,.0f} RUB (через {car['proxy']})")
