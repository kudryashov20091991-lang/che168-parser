#!/usr/bin/env python3
import requests, re, json, time
from datetime import datetime

PROXIES = [
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13851", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13851"},
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13852", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13852"},
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13853", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13853"},
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def parse():
    cars = []
    results = []
    for proxy in PROXIES:
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
    return cars, results

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    cars, results = parse()
    print(f"Found: {len(cars)} cars")
    output = {
        "timestamp": datetime.now().isoformat(),
        "source": "che168.com",
        "proxies_tested": len(PROXIES),
        "cars_found": len(cars),
        "results": results,
        "cars": cars
    }
    with open("che168_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
