"""
Получение рабочих прокси и парсинг che168
"""

import requests
import json
from pathlib import Path

print("=" * 60)
print("ПОЛУЧЕНИЕ РАБОЧИХ ПРОКСИ")
print("=" * 60)

# Источник 1: spys.me
try:
    resp = requests.get("https://raw.githubusercontent.com/spysme/proxy-list/main/proxy-list.txt", timeout=10)
    if resp.status_code == 200:
        lines = resp.text.strip().split("\n")[:50]
        print(f"spys.me: {len(lines)} прокси")
except Exception as e:
    print(f"spys.me error: {e}")

# Источник 2: proxyscrape API
try:
    resp = requests.get(
        "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http&proxy_format=ipport&format=json",
        timeout=10
    )
    if resp.status_code == 200:
        data = resp.json()
        proxies_scrape = data.get("proxies", [])[:20]
        print(f"proxyscrape: {len(proxies_scrape)} прокси")
        for p in proxies_scrape[:5]:
            print(f"  {p.get('ip', '')}:{p.get('port', '')}")
except Exception as e:
    print(f"proxyscrape error: {e}")

# Источник 3: geonode
try:
    resp = requests.get(
        "https://proxylist.geonode.com/api/proxy-list?limit=20&page=1&sort_by=lastChecked&sort_type=desc&protocols=http",
        timeout=10
    )
    if resp.status_code == 200:
        data = resp.json()
        geonode_proxies = data.get("data", [])
        print(f"geonode: {len(geonode_proxies)} прокси")
        for p in geonode_proxies[:5]:
            print(f"  {p.get('ip', '')}:{p.get('port', '')} | {p.get('country', '')}")
except Exception as e:
    print(f"geonode error: {e}")

print("\n" + "=" * 60)
print("Прокси 45.32.56.105:1385X - НЕ РАБОЧИЕ (проверено)")
print("Нужны актуальные прокси от пользователя")
print("=" * 60)
