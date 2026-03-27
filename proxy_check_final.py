"""
Проверка прокси разными способами
Прокси: 45.32.56.105:13851/52/53
Auth: Ek0G8F:GR0Fhj
"""

import requests
import time

PROXIES = [
    {"host": "45.32.56.105", "port": "13851"},
    {"host": "45.32.56.105", "port": "13852"},
    {"host": "45.32.56.105", "port": "13853"},
]
USER = "Ek0G8F"
PASS = "GR0Fhj"

def check_format(format_name, proxy_dict):
    """Проверка конкретного формата прокси"""
    try:
        resp = requests.get("https://httpbin.org/ip", proxies=proxy_dict, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            return True, data.get('origin', 'unknown')
        return False, f"Status: {resp.status_code}"
    except Exception as e:
        return False, str(e)[:80]

print("=" * 60)
print("ПРОВЕРКА ВСЕХ ФОРМАТОВ ПРОКСИ")
print("=" * 60)

formats_to_test = [
    ("HTTP с авторизацией в URL", lambda h, p: {
        "http": f"http://{USER}:{PASS}@{h}:{p}",
        "https": f"http://{USER}:{PASS}@{h}:{p}"
    }),
    ("HTTPS с авторизацией в URL", lambda h, p: {
        "http": f"https://{USER}:{PASS}@{h}:{p}",
        "https": f"https://{USER}:{PASS}@{h}:{p}"
    }),
    ("SOCKS5 с авторизацией в URL", lambda h, p: {
        "http": f"socks5://{USER}:{PASS}@{h}:{p}",
        "https": f"socks5://{USER}:{PASS}@{h}:{p}"
    }),
    ("SOCKS4 с авторизацией в URL", lambda h, p: {
        "http": f"socks4://{USER}:{PASS}@{h}:{p}",
        "https": f"socks4://{USER}:{PASS}@{h}:{p}"
    }),
    ("Без авторизации (если IP белый)", lambda h, p: {
        "http": f"http://{h}:{p}",
        "https": f"http://{h}:{p}"
    }),
]

# Сначала попробуем установить socks библиотеку
try:
    import socks
    print("SOCKS библиотека доступна")
except ImportError:
    print("Установка PySocks...")
    import subprocess
    subprocess.run(["pip", "install", "pysocks", "-q"])
    try:
        import socks
        print("SOCKS библиотека установлена")
    except:
        print("SOCKS библиотека не доступна")

for format_name, format_func in formats_to_test:
    print(f"\n{format_name}:")
    for i, p in enumerate(PROXIES):
        addr = f"{p['host']}:{p['port']}"
        proxy_dict = format_func(p['host'], p['port'])
        ok, result = check_format(format_name, proxy_dict)
        status = "OK" if ok else "FAIL"
        print(f"  [{i+1}] {addr}: {status} - {result}")
        if ok:
            print(f"      РАБОЧИЙ ПРОКСИ НАЙДЕН!")
            break  # Если первый работает, не проверяем остальные для этого формата
    time.sleep(0.5)

print("\n" + "=" * 60)
print("ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 60)
