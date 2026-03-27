#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки прокси от провайдеров
Используется для тестирования купленных прокси
"""

import requests
from requests.auth import HTTPProxyAuth
import json
import concurrent.futures
from typing import List, Dict, Optional

# Пример конфигурации прокси (замените на свои данные после покупки)
# Smartproxy пример:
SMARTPROXY_CONFIG = {
    "gateway": "gate.smartproxy.com",
    "port": 10000,
    "username": "sp_user_XXXXXXXXXX",  # Заменить на ваш
    "password": "XXXXXXXXXX",          # Заменить на ваш
}

# IPRoyal пример:
IPROYAL_CONFIG = {
    "gateway": "proxy.iproyal.com",
    "port": 12321,
    "username": "XXXXXXXXXX",
    "password": "XXXXXXXXXX",
}

# Oxylabs пример:
OXYLABS_CONFIG = {
    "gateway": "pr.oxylabs.io",
    "port": 7777,
    "username": "XXXXXXXXXX",
    "password": "XXXXXXXXXX",
}

def print_safe(text):
    """Безопасный вывод с поддержкой кириллицы"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp1251', errors='replace').decode('cp1251'))

def check_single_proxy(proxy_config: Dict, proxy_name: str = "Proxy") -> Dict:
    """
    Проверка одного прокси

    Returns:
        Dict с результатами: {'name': str, 'ip': str, 'country': str, 'success': bool, 'error': str}
    """
    result = {
        'name': proxy_name,
        'ip': None,
        'country': None,
        'success': False,
        'error': None
    }

    proxies = {
        "http": f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['gateway']}:{proxy_config['port']}",
        "https": f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['gateway']}:{proxy_config['port']}",
    }

    try:
        # Проверка IP
        response = requests.get(
            "https://api.ipify.org?format=json",
            proxies=proxies,
            timeout=15
        )

        if response.status_code == 200:
            ip_data = response.json()
            result['ip'] = ip_data.get('ip')
            result['success'] = True

            # Получение информации о стране (опционально)
            try:
                geo_response = requests.get(
                    f"https://ipapi.co/{result['ip']}/json/",
                    timeout=10
                )
                if geo_response.status_code == 200:
                    geo_data = geo_response.json()
                    result['country'] = geo_data.get('country_name')
            except:
                pass

            print_safe(f"[OK] {proxy_name}: IP={result['ip']}, Country={result['country']}")
        else:
            result['error'] = f"HTTP {response.status_code}"
            print_safe(f"[ERROR] {proxy_name}: {result['error']}")

    except requests.exceptions.ProxyError as e:
        result['error'] = f"Proxy Error: {str(e)}"
        print_safe(f"[ERROR] {proxy_name}: Proxy Error - {str(e)[:50]}")
    except requests.exceptions.Timeout:
        result['error'] = "Timeout"
        print_safe(f"[ERROR] {proxy_name}: Timeout")
    except Exception as e:
        result['error'] = str(e)[:100]
        print_safe(f"[ERROR] {proxy_name}: {str(e)[:50]}")

    return result

def check_proxy_list(proxy_list: List[Dict]) -> List[Dict]:
    """
    Проверка списка прокси

    Args:
        proxy_list: Список словарей с конфигурацией прокси

    Returns:
        Список результатов проверки
    """
    results = []

    print_safe(f"\nПроверка {len(proxy_list)} прокси...\n")

    # Последовательная проверка
    for i, proxy in enumerate(proxy_list):
        proxy_name = proxy.get('name', f"Proxy #{i+1}")
        config = proxy.get('config', proxy)
        result = check_single_proxy(config, proxy_name)
        results.append(result)

    return results

def check_proxy_rotation(proxy_config: Dict, num_checks: int = 10) -> Dict:
    """
    Проверка ротации IP у прокси-провайдера

    Returns:
        Dict со статистикой ротации
    """
    print_safe(f"\nПроверка ротации IP ({num_checks} запросов)...")

    ips = set()
    successful_requests = 0

    for i in range(num_checks):
        proxies = {
            "http": f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['gateway']}:{proxy_config['port']}",
            "https": f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['gateway']}:{proxy_config['port']}",
        }

        try:
            response = requests.get(
                "https://api.ipify.org?format=json",
                proxies=proxies,
                timeout=15
            )

            if response.status_code == 200:
                ip = response.json().get('ip')
                ips.add(ip)
                successful_requests += 1
                print_safe(f"  Запрос {i+1}: IP={ip}")

        except Exception as e:
            print_safe(f"  Запрос {i+1}: Ошибка - {str(e)[:50]}")

    # Статистика
    result = {
        'total_requests': num_checks,
        'successful_requests': successful_requests,
        'unique_ips': len(ips),
        'success_rate': f"{successful_requests/num_checks*100:.1f}%",
        'unique_ips_list': list(ips),
    }

    print_safe(f"\nРезультаты ротации:")
    print_safe(f"  Успешных запросов: {successful_requests}/{num_checks} ({result['success_rate']})")
    print_safe(f"  Уникальных IP: {len(ips)}")
    if len(ips) > 1:
        print_safe(f"  [OK] Ротация работает! IP меняются.")
    else:
        print_safe(f"  [WARN] Все запросы с одного IP (возможно, сессионная ротация)")

    return result

def test_target_site(proxy_config: Dict, target_url: str, target_name: str) -> Dict:
    """
    Тест доступа к целевому сайту через прокси

    Args:
        proxy_config: Конфигурация прокси
        target_url: URL сайта для теста
        target_name: Название сайта для отчета
    """
    print_safe(f"\nТест доступа к {target_name} ({target_url})...")

    proxies = {
        "http": f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['gateway']}:{proxy_config['port']}",
        "https": f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['gateway']}:{proxy_config['port']}",
    }

    try:
        response = requests.get(
            target_url,
            proxies=proxies,
            timeout=30,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

        result = {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response_size': len(response.content),
            'time_ms': response.elapsed.total_seconds() * 1000,
        }

        print_safe(f"  Статус: {response.status_code}")
        print_safe(f"  Размер ответа: {len(response.content)} байт")
        print_safe(f"  Время: {result['time_ms']:.0f} мс")

        if response.status_code == 200:
            print_safe(f"  [OK] {target_name} доступен!")
        else:
            print_safe(f"  [WARN] {target_name} вернул статус {response.status_code}")

        return result

    except Exception as e:
        print_safe(f"  [ERROR] {target_name}: {str(e)[:100]}")
        return {
            'success': False,
            'error': str(e)[:100]
        }

def main():
    """
    Основная функция
    """
    print_safe("=" * 70)
    print_safe("ПРОВЕРКА ПРОКСИ ДЛЯ ПАРСИНГА АВТОСАЙТОВ")
    print_safe("=" * 70)

    # Меню
    print_safe("""
Выберите действие:

1. Проверить список прокси (нужно добавить конфигурацию в скрипт)
2. Проверить ротацию IP (нужно добавить конфигурацию в скрипт)
3. Тест доступа к che168.com
4. Тест доступа к dongchedi.com
5. Тест доступа к encar.com
6. Выход
""")

    # Для демонстрации - проверка без реальных прокси
    print_safe("\n[INFO] Для работы скрипта добавьте ваши прокси в конфигурацию:")
    print_safe("  - SMARTPROXY_CONFIG")
    print_safe("  - IPROYAL_CONFIG")
    print_safe("  - OXYLABS_CONFIG")
    print_safe("\nПосле покупки прокси замените placeholder значения на реальные.")

    # Пример проверки (будет ошибка без реальных прокси)
    print_safe("\n" + "=" * 70)
    print_safe("ПРИМЕР ПРОВЕРКИ (ожидайте ошибку без реальных прокси)")
    print_safe("=" * 70)

    # Тест с dummy конфигурацией
    dummy_config = {
        "gateway": "gate.smartproxy.com",
        "port": 10000,
        "username": "demo_user",
        "password": "demo_pass",
    }

    print_safe("\nПроверка IP (демо конфигурация)...")
    result = check_single_proxy(dummy_config, "Demo Proxy")
    print_safe(f"Результат: {result}")

    print_safe("\n" + "=" * 70)
    print_safe("ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ:")
    print_safe("=" * 70)
    print_safe("""
1. Купите прокси у одного из провайдеров:
   - Smartproxy (smartproxy.com) - от $75/мес, 20GB
   - IPRoyal (iproyal.com) - от $20/мес, бюджетный вариант
   - Oxylabs (oxylabs.io) - от $300/мес, премиум
   - Bright Data (brightdata.com) - от $300/мес, премиум

2. После получения доступов отредактируйте этот скрипт:
   - Замените SMARTPROXY_CONFIG на ваши данные
   - Или добавьте новую конфигурацию

3. Запустите скрипт для проверки:
   - Проверка IP каждого прокси
   - Проверка ротации IP
   - Тест доступа к целевым сайтам (che168, dongchedi, encar)

4. Интегрируйте рабочие прокси в код парсера
""")

if __name__ == "__main__":
    main()
