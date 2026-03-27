"""Проверка прокси перед парсингом"""
import requests

PROXIES = [
    {"server": "45.32.56.105:13851", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "45.32.56.105:13852", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "45.32.56.105:13853", "username": "Ek0G8F", "password": "GR0Fhj"},
]

print("=" * 60)
print("ПРОВЕРКА ПРОКСИ")
print("=" * 60)

for i, proxy in enumerate(PROXIES):
    print(f"\n[Прокси {i+1}] {proxy['server']}")

    proxies = {
        "http": f"http://{proxy['username']}:{proxy['password']}@{proxy['server']}",
        "https": f"http://{proxy['username']}:{proxy['password']}@{proxy['server']}",
    }

    try:
        response = requests.get(
            "https://api.ipify.org?format=json",
            proxies=proxies,
            timeout=15
        )
        if response.status_code == 200:
            ip = response.json().get("ip", "не определен")
            print(f"  СТАТУС: РАБОТАЕТ")
            print(f"  IP: {ip}")
        else:
            print(f"  СТАТУС: ОШИБКА {response.status_code}")
    except Exception as e:
        print(f"  СТАТУС: НЕ РАБОТАЕТ")
        print(f"  Ошибка: {str(e)[:100]}")

print("\n" + "=" * 60)
