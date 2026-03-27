#!/usr/bin/env python3
"""
Скрипт для проверки IP адресов поддоменов на Beget

Как использовать:
1. Создайте поддомены в панели Beget:
   - proxy1.best-japan-cars.ru
   - proxy2.best-japan-cars.ru
   - ...
   - proxy10.best-japan-cars.ru

2. Запустите скрипт:
   python check_proxy_ips.py

3. Скрипт покажет IP каждого поддомена и сравнит их
"""

import socket
import json
from datetime import datetime

# Список поддоменов для проверки
# ЗАМЕНИТЕ на ваши реальные поддомены!
SUBDOMAINS = [
    "proxy1.best-japan-cars.ru",
    "proxy2.best-japan-cars.ru",
    "proxy3.best-japan-cars.ru",
    "proxy4.best-japan-cars.ru",
    "proxy5.best-japan-cars.ru",
    "proxy6.best-japan-cars.ru",
    "proxy7.best-japan-cars.ru",
    "proxy8.best-japan-cars.ru",
    "proxy9.best-japan-cars.ru",
    "proxy10.best-japan-cars.ru",
]

def get_ip(domain):
    """Получить IP адрес домена"""
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror as e:
        return f"Ошибка: {e}"

def check_all_ips():
    """Проверить все поддомены"""
    print("=" * 60)
    print("ПРОВЕРКА IP АДРЕСОВ ПОДДОМЕНОВ")
    print("=" * 60)
    print(f"Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []
    ip_counts = {}

    for subdomain in SUBDOMAINS:
        ip = get_ip(subdomain)
        results.append((subdomain, ip))

        # Подсчёт количества поддоменов на каждом IP
        if ip not in ip_counts:
            ip_counts[ip] = []
        ip_counts[ip].append(subdomain)

    # Вывод результатов
    print("Результаты:")
    print("-" * 60)
    print(f"{'Поддомен':<35} {'IP адрес':<20}")
    print("-" * 60)

    for subdomain, ip in results:
        print(f"{subdomain:<35} {ip:<20}")

    print()
    print("=" * 60)
    print("СВОДКА ПО IP АДРЕСАМ")
    print("=" * 60)

    unique_ips = set(ip for _, ip in results if not ip.startswith("Ошибка"))

    print(f"\nВсего поддоменов: {len(SUBDOMAINS)}")
    print(f"Уникальных IP: {len(unique_ips)}")
    print()

    if len(unique_ips) == len(SUBDOMAINS):
        print("✅ ОТЛИЧНО! Все поддомены имеют разные IP адреса!")
        print("   Можно использовать как прокси для парсинга.")
    elif len(unique_ips) >= len(SUBDOMAINS) // 2:
        print(f"⚠️ НОРМАЛЬНО! {len(unique_ips)} из {len(SUBDOMAINS)} имеют уникальные IP")
        print("   Можно использовать, но некоторые IP повторяются.")
    else:
        print(f"❌ ПЛОХО! Только {len(unique_ips)} уникальных IP из {len(SUBDOMAINS)}")
        print("   Большинство поддоменов на одном IP - будут проблемы с парсингом!")

    print()
    print("Распределение по IP:")
    print("-" * 60)

    for ip, domains in sorted(ip_counts.items(), key=lambda x: -len(x[1])):
        if ip.startswith("Ошибка"):
            continue
        count = len(domains)
        status = "✅" if count == 1 else "⚠️"
        print(f"{status} {ip}: {count} поддомен(ов)")
        if count > 1:
            for d in domains:
                print(f"      - {d}")

    print()
    print("=" * 60)

    # Сохранение результатов в файл
    output_file = "ip_check_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "total_subdomains": len(SUBDOMAINS),
            "unique_ips": len(unique_ips),
            "results": results,
            "ip_distribution": {k: v for k, v in ip_counts.items() if not k.startswith("Ошибка")}
        }, f, ensure_ascii=False, indent=2)

    print(f"\nРезультаты сохранены в файл: {output_file}")
    print()

if __name__ == "__main__":
    check_all_ips()
