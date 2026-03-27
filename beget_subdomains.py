#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания поддоменов в Beget через HTTP API с Basic Auth
"""

import requests
from requests.auth import HTTPBasicAuth
import json

# Доступы к Beget
BEGET_LOGIN = "ahilesor"
BEGET_PASSWORD = "TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:`"

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

def create_subdomains_http():
    """Создание поддоменов через HTTP запросы с Basic Auth"""

    print_safe("=" * 60)
    print_safe("СОЗДАНИЕ ПОДДОМЕНОВ ЧЕРЕЗ BEGET API (Basic Auth)")
    print_safe("=" * 60)

    # Создаем сессию с Basic Auth
    session = requests.Session()
    session.auth = HTTPBasicAuth(BEGET_LOGIN, BEGET_PASSWORD)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    })

    # 1. Тест авторизации
    print_safe("\n[1] Тест авторизации...")

    try:
        response = session.get(
            "https://cp.beget.com/api/auth/user",
            timeout=10
        )
        print_safe(f"Status: {response.status_code}")
        print_safe(f"Content-Type: {response.headers.get('Content-Type')}")
        print_safe(f"Response: {response.text[:300]}")

        if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('application/json'):
            user_data = response.json()
            print_safe(f"[OK] Авторизация успешна! Пользователь: {user_data.get('user', 'unknown')}")
        else:
            print_safe("[WARN] Авторизация может не работать")
    except Exception as e:
        print_safe(f"Ошибка: {e}")

    # 2. Получение списка доменов
    print_safe("\n[2] Получение списка доменов...")

    try:
        response = session.get(
            "https://cp.beget.com/api/domain/list",
            timeout=10
        )
        print_safe(f"Status: {response.status_code}")
        print_safe(f"Response: {response.text[:500]}")
    except Exception as e:
        print_safe(f"Ошибка: {e}")

    # 3. Создание поддоменов
    print_safe("\n[3] Создание поддоменов...")

    created = []
    for subdomain in SUBDOMAINS:
        print_safe(f"\nПопытка создания: {subdomain}.{MAIN_DOMAIN}")

        try:
            # Используем правильный формат API Beget
            response = session.post(
                "https://cp.beget.com/api/domain/subdomain/add",
                json={
                    "domain": MAIN_DOMAIN,
                    "subdomain": subdomain,
                },
                timeout=30
            )

            print_safe(f"Status: {response.status_code}")
            print_safe(f"Content-Type: {response.headers.get('Content-Type')}")
            print_safe(f"Response: {response.text[:500]}")

            # Проверяем ответ
            if response.status_code == 200:
                try:
                    result = response.json()
                    print_safe(f"JSON result: {result}")

                    # Проверяем успешность
                    if result.get("status") == "success" or result.get("error") is None:
                        print_safe(f"[OK] Поддомен создан!")
                        created.append(subdomain)
                    elif "already exists" in str(result).lower() or "существует" in str(result).lower():
                        print_safe(f"[INFO] Поддомен уже существует")
                        created.append(subdomain)
                except Exception as e:
                    print_safe(f"Ошибка парсинга JSON: {e}")

        except Exception as e:
            print_safe(f"Ошибка создания: {e}")

    print_safe(f"\nИтого создано: {len(created)}/{len(SUBDOMAINS)}")
    print_safe("Созданные поддомены: " + str(created))

    return created

def main():
    try:
        create_subdomains_http()
    except Exception as e:
        print_safe(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
