"""Детальная проверка прокси"""
import requests
import time

PROXIES = [
    {"host": "45.32.56.105", "port": "13851", "user": "Ek0G8F", "pass": "GR0Fhj"},
    {"host": "45.32.56.105", "port": "13852", "user": "Ek0G8F", "pass": "GR0Fhj"},
    {"host": "45.32.56.105", "port": "13853", "user": "Ek0G8F", "pass": "GR0Fhj"},
]

print("=" * 60)
print("ДЕТАЛЬНАЯ ПРОВЕРКА ПРОКСИ")
print("=" * 60)

for i, p in enumerate(PROXIES):
    print(f"\n[Прокси {i+1}] {p['host']}:{p['port']}")

    # Формат 1: HTTP с авторизацией в URL
    proxy_http = f"http://{p['user']}:{p['pass']}@{p['host']}:{p['port']}"

    # Формат 2: SOCKS5
    proxy_socks = f"socks5://{p['user']}:{p['pass']}@{p['host']}:{p['port']}"

    # Формат 3: SOCKS5 без пароля в URL (отдельно)
    proxy_socks2 = f"socks5://{p['host']}:{p['port']}"

    formats = [
        ("HTTP auth", proxy_http),
        ("SOCKS5 auth", proxy_socks),
        ("SOCKS5 no auth", proxy_socks2),
    ]

    for name, proxy_url in formats:
        try:
            proxies = {"http": proxy_url, "https": proxy_url}
            print(f"  {name}: ", end="", flush=True)

            start = time.time()
            resp = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=8)
            elapsed = time.time() - start

            if resp.status_code == 200:
                data = resp.json()
                print(f"OK ({elapsed:.2f}s) - IP: {data.get('origin', 'unknown')}")
            else:
                print(f"FAIL (status {resp.status_code})")
        except requests.exceptions.ProxyError as e:
            print(f"PROXY ERROR: {str(e)[:50]}")
        except requests.exceptions.ConnectTimeout:
            print(f"CONNECT TIMEOUT")
        except Exception as e:
            print(f"ERROR: {str(e)[:50]}")

print("\n" + "=" * 60)
