"""
Быстрая проверка прокси с таймаутом 3 секунды
"""

import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import time

PROXIES = [
    "45.32.56.105:13851",
    "45.32.56.105:13852",
    "45.32.56.105:13853",
]
USER = "Ek0G8F"
PASS = "GR0Fhj"

def check_single_proxy(proxy_addr):
    """Проверка одного прокси"""
    proxy_dict = {
        "http": f"http://{USER}:{PASS}@{proxy_addr}",
        "https": f"http://{USER}:{PASS}@{proxy_addr}"
    }
    try:
        resp = requests.get("https://httpbin.org/ip", proxies=proxy_dict, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            return True, data.get('origin', 'unknown')
        return False, f"Status {resp.status_code}"
    except Exception as e:
        return False, str(e)[:50]

def check_with_timeout(proxy_addr, timeout_sec=3):
    """Проверка с таймаутом через ThreadPool"""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(check_single_proxy, proxy_addr)
        try:
            return future.result(timeout=timeout_sec)
        except TimeoutError:
            return False, "Timeout (прокси не отвечает)"
        except Exception as e:
            return False, str(e)[:50]

print("=" * 60)
print("БЫСТРАЯ ПРОВЕРКА ПРОКСИ (3 сек на каждый)")
print("=" * 60)

working = []
for addr in PROXIES:
    print(f"Проверка {addr}...", end=" ", flush=True)
    ok, result = check_with_timeout(addr, timeout_sec=3)
    if ok:
        print(f"OK - IP: {result}")
        working.append(addr)
    else:
        print(f"FAIL - {result}")

print(f"\nРабочих: {len(working)} из {len(PROXIES)}")
if working:
    print(f"Рабочие прокси: {working}")
else:
    print("НИ ОДИН ПРОКСИ НЕ РАБОТАЕТ!")
    print("\nВозможные причины:")
    print("  1. Прокси требуют подключения с определенного IP")
    print("  2. Неверный формат авторизации")
    print("  3. Прокси истекли/заблокированы")
    print("\nНужны актуальные данные прокси!")

print("=" * 60)
