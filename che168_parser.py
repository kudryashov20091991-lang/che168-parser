#!/usr/bin/env python3
"""
Che168 parser for GitHub Actions
Runs on GitHub's cloud servers - no VPN restrictions
Tries multiple endpoints and fallback sites
"""
import requests, re, json, time, os
from datetime import datetime

# Прокси для локального запуска (опционально)
PROXIES = [
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13851", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13851"},
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13852", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13852"},
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13853", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13853"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# Альтернативные URL для парсинга
URLS = [
    "https://www.che168.com/beijing/",
    "https://m.che168.com/beijing/",  # Mobile version
    "https://www.che168.com/api/beijing/list",  # API endpoint (if exists)
]

def parse_url(url, proxy=None):
    """Try to parse cars from a single URL"""
    cars = []
    try:
        kwargs = {"headers": HEADERS, "timeout": 60, "verify": False}
        if proxy:
            kwargs["proxies"] = proxy
        resp = requests.get(url, **kwargs)
        if resp.status_code != 200:
            return cars, None

        # Try to find JSON data in the response
        json_matches = re.findall(r'\{[^{}]*"price"[^{}]*\}', resp.text)
        for match in json_matches:
            try:
                price_match = re.search(r'"price"\s*:\s*"?(\d+\.?\d*)"?', match)
                if price_match:
                    val = float(price_match.group(1))
                    if 0.1 < val < 100:
                        cars.append({"price_cny": val * 10000, "price_rub": round(val * 10000 * 13, 2)})
            except: pass

        # Try traditional patterns
        prices = re.findall(r'(\d+\.?\d*)\s*万', resp.text)
        for p in prices[:10]:
            try:
                val = float(p)
                cars.append({"price_cny": val * 10000, "price_rub": round(val * 10000 * 13, 2)})
            except: pass

    except Exception as e:
        pass
    return cars, resp.text[:50000] if 'resp' in dir() else None

def parse():
    cars = []
    results = []
    debug_html = ""

    # На GitHub Actions пробуем без прокси сначала
    if os.environ.get("GITHUB_ACTIONS") == "true":
        for url in URLS:
            if cars:
                break
            result = {"proxy": "direct", "url": url, "status": "error", "error": ""}
            try:
                found, html = parse_url(url)
                if found:
                    cars.extend(found[:10])
                    result["status"] = "success"
                    debug_html = html
                else:
                    result["error"] = "No cars found"
            except Exception as e:
                result["error"] = str(e)[:100]
            results.append(result)

    # Если не удалось или локальный запуск - пробуем прокси
    if not cars:
        for proxy in PROXIES:
            if len(cars) >= 10: break
            proxy_host = proxy["http"].split("@")[1]
            result = {"proxy": proxy_host, "status": "error", "error": ""}
            try:
                resp = requests.get("https://www.che168.com/beijing/", proxies=proxy, headers=HEADERS, timeout=60, verify=False)
                if resp.status_code == 200:
                    result["status"] = "success"
                    prices = re.findall(r'"price":"(\d+\.?\d*)"', resp.text) + re.findall(r'(\d+\.?\d*)\s*万', resp.text)
                    for p in prices:
                        if len(cars) < 10:
                            price_cny = float(p) * 10000
                            cars.append({"price_cny": price_cny, "price_rub": round(price_cny * 13, 2), "proxy": proxy_host})
            except requests.exceptions.Timeout:
                result["error"] = f"Timeout ({proxy_host})"
            except requests.exceptions.ProxyError as e:
                result["error"] = f"Proxy error: {str(e)[:50]}"
            except Exception as e:
                result["error"] = str(e)[:100]
            results.append(result)
            time.sleep(2)

    return cars, results, debug_html

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    cars, results, debug_html = parse()
    print(f"Found: {len(cars)} cars")
    output = {
        "timestamp": datetime.now().isoformat(),
        "source": "che168.com",
        "proxies_tested": len(PROXIES) + 1 if os.environ.get("GITHUB_ACTIONS") == "true" else len(PROXIES),
        "cars_found": len(cars),
        "results": results,
        "cars": cars
    }
    with open("che168_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Сохраняем debug HTML как артефакт
    if os.environ.get("GITHUB_ACTIONS") == "true" and debug_html:
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(debug_html)
