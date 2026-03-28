#!/usr/bin/env python3
import requests, re, json, time
from datetime import datetime

PROXIES = [
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13851", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13851"},
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13852", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13852"},
    {"http": "http://Ek0G8F:GR0Fhj@45.32.56.105:13853", "https": "http://Ek0G8F:GR0Fhj@45.32.56.105:13853"},
]
HEADERS = {"User-Agent": "Mozilla/5.0"}

def parse():
    cars = []
    for proxy in PROXIES:
        if len(cars) >= 10: break
        try:
            resp = requests.get("https://www.che168.com/beijing/", proxies=proxy, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                for p in re.findall(r"(\d+\.?\d*)\s*", resp.text):
                    if len(cars) < 10:
                        cars.append({"price_cny": float(p)*10000, "price_rub": round(float(p)*10000*13, 2), "proxy": proxy["http"].split("@")[1]})
        except: pass
        time.sleep(1)
    return cars

if __name__ == "__main__":
    result = parse()
    print(f"Found: {len(result)} cars")
    with open("che168_result.json", "w", encoding="utf-8") as f:
        json.dump({"time": datetime.now().isoformat(), "cars": result}, f, indent=2, ensure_ascii=False)
