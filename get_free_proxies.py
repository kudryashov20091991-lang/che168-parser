"""Получение списка бесплатных прокси"""
import requests
from bs4 import BeautifulSoup

def get_free_proxies():
    """Скачиваем прокси с нескольких источников"""
    proxies = []

    # Источник 1: geonode
    try:
        resp = requests.get("https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for p in data.get('data', []):
                if p.get('anonymity') in ['elite', 'anonymous'] and p.get('protocols') and 'http' in p.get('protocols', []):
                    proxies.append({
                        "host": p['ip'],
                        "port": str(p['port']),
                        "username": "",
                        "password": ""
                    })
    except Exception as e:
        print(f"Geonode error: {e}")

    # Источник 2: api.proxyscrape
    try:
        resp = requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&protocol=http&proxy_format=protocolipport&format=json", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for p in data.get('proxies', []):
                proxies.append({
                    "host": p.get('ip', ''),
                    "port": str(p.get('port', '')),
                    "username": "",
                    "password": ""
                })
    except Exception as e:
        print(f"ProxyScrape error: {e}")

    print(f"Найдено прокси: {len(proxies)}")
    return proxies[:20]  # Возвращаем первые 20

if __name__ == "__main__":
    proxies = get_free_proxies()
    for p in proxies[:5]:
        print(f"  {p['host']}:{p['port']}")
