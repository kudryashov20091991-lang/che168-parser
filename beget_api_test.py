#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования API Beget и создания поддоменов
"""

import requests
import json
from requests.auth import HTTPBasicAuth
import sys

# Доступы к Beget
BEGET_LOGIN = "ahilesor"
BEGET_PASSWORD = "TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:`"

# Базовый URL API Beget
API_BASE = "https://api.beget.com"
CP_BASE = "https://cp.beget.com"

# Основной домен
MAIN_DOMAIN = "luchshie-yaponskie-avto.ru"

# Названия для поддоменов
SUBDOMAINS = [
    "japan-auto1",
    "japan-auto2",
    "japan-auto3",
    "japan-auto4",
    "japan-auto5",
    "japan-auto6",
    "japan-auto7",
    "japan-auto8",
    "japan-auto9",
    "japan-auto10",
]

def print_safe(text):
    """Безопасный вывод с поддержкой кириллицы"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('cp1251', errors='replace').decode('cp1251'))

def test_api_auth():
    """Тест авторизации в API"""
    print_safe("=== Тест авторизации в API Beget ===")

    # Пробуем разные варианты авторизации
    endpoints_to_try = [
        f"{API_BASE}/v1/user",
        f"{CP_BASE}/api/user",
        f"{CP_BASE}/api/v1/user",
    ]

    for url in endpoints_to_try:
        print_safe(f"\nПроверка: {url}")
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(BEGET_LOGIN, BEGET_PASSWORD),
                timeout=10
            )
            print_safe(f"Status: {response.status_code}")
            print_safe(f"Response: {response.text[:500]}")

            if response.status_code == 200:
                print_safe("[OK] Авторизация успешна!")
                return True
        except Exception as e:
            print_safe(f"Ошибка: {e}")

    return False

def get_subdomains():
    """Получить список существующих поддоменов"""
    print_safe("\n=== Получение списка поддоменов ===")

    # Пробуем разные эндпоинты
    endpoints = [
        f"{API_BASE}/v1/subdomain/list",
        f"{API_BASE}/v1/subdomain",
        f"{CP_BASE}/api/subdomain/list",
    ]

    for url in endpoints:
        print_safe(f"\nПроверка: {url}")
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(BEGET_LOGIN, BEGET_PASSWORD),
                timeout=10
            )
            print_safe(f"Status: {response.status_code}")
            print_safe(f"Response: {response.text[:1000]}")

            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    pass
        except Exception as e:
            print_safe(f"Ошибка: {e}")

    return None

def create_subdomain(subdomain_name):
    """Создать поддомен"""
    print_safe(f"\n=== Создание поддомена: {subdomain_name}.{MAIN_DOMAIN} ===")

    # Пробуем разные эндпоинты
    endpoints = [
        f"{API_BASE}/v1/subdomain/add",
        f"{CP_BASE}/api/subdomain/add",
    ]

    data = {
        "domain": MAIN_DOMAIN,
        "subdomain": subdomain_name,
    }

    for url in endpoints:
        print_safe(f"URL: {url}")
        try:
            response = requests.post(
                url,
                auth=HTTPBasicAuth(BEGET_LOGIN, BEGET_PASSWORD),
                json=data,
                timeout=30
            )
            print_safe(f"Status: {response.status_code}")
            print_safe(f"Response: {response.text[:500]}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("result") == "success" or result.get("error") is None:
                        print_safe(f"[OK] Поддомен {subdomain_name}.{MAIN_DOMAIN} создан!")
                        return True
                except:
                    pass

            print_safe(f"[ERROR] Ошибка создания поддомена")
        except Exception as e:
            print_safe(f"Ошибка: {e}")

    return False

def check_proxy_ip(proxy_url, proxy_port, proxy_user=None, proxy_pass=None):
    """Проверить IP прокси"""
    print_safe(f"\nПроверка прокси: {proxy_url}:{proxy_port}")

    proxies = {
        "http": f"http://{proxy_user}:{proxy_pass}@{proxy_url}:{proxy_port}" if proxy_user else f"http://{proxy_url}:{proxy_port}",
        "https": f"http://{proxy_user}:{proxy_pass}@{proxy_url}:{proxy_port}" if proxy_user else f"http://{proxy_url}:{proxy_port}",
    }

    try:
        response = requests.get(
            "https://api.ipify.org?format=json",
            proxies=proxies,
            timeout=10
        )
        if response.status_code == 200:
            ip = response.json().get("ip")
            print_safe(f"[OK] IP прокси: {ip}")
            return ip
    except Exception as e:
        print_safe(f"[ERROR] Ошибка: {e}")

    return None

def main():
    print_safe("=" * 60)
    print_safe("ТЕСТИРОВАНИЕ API BEGET И СОЗДАНИЕ ПОДДОМЕНОВ")
    print_safe("=" * 60)

    # 1. Тест авторизации
    auth_success = test_api_auth()

    if not auth_success:
        print_safe("\n[ERROR] Не удалось авторизоваться в API Beget")
        print_safe("Попробуем альтернативные методы...")

    # 2. Получение списка поддоменов
    get_subdomains()

    # 3. Создание поддоменов
    print_safe("\n" + "=" * 60)
    print_safe("СОЗДАНИЕ ПОДДОМЕНОВ")
    print_safe("=" * 60)

    created = []
    for subdomain in SUBDOMAINS:
        if create_subdomain(subdomain):
            created.append(subdomain)

    print_safe(f"\nИтого создано: {len(created)}/{len(SUBDOMAINS)}")
    print_safe("Созданные поддомены: " + str(created))

if __name__ == "__main__":
    main()
