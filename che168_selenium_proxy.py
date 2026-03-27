"""
Парсер che168.com через Selenium + прокси
Альтернатива Playwright
"""

import time
import json
import re
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROXIES = [
    "45.32.56.105:13851:Ek0G8F:GR0Fhj",
    "45.32.56.105:13852:Ek0G8F:GR0Fhj",
    "45.32.56.105:13853:Ek0G8F:GR0Fhj",
]

ZH_RU = {
    "万公里": " тыс. км", "年": " г.", "北京": "Пекин",
    "奔驰": "Mercedes-Benz", "宝马": "BMW", "奥迪": "Audi",
    "保时捷": "Porsche", "路虎": "Land Rover",
}

def translate(t):
    for z, r in ZH_RU.items(): t = t.replace(z, r)
    return t

def parse_with_selenium():
    print("=" * 60)
    print("ПАРСИНГ CHE168.COM - SELENIUM + ПРОКСИ")
    print("=" * 60)

    all_cars = []

    for attempt, proxy_str in enumerate(PROXIES * 10):  # Ротация
        if len(all_cars) >= 10:
            break

        print(f"\n[Попытка {attempt+1}] Прокси: {proxy_str}")

        try:
            # Настройка прокси
            proxy_parts = proxy_str.split(":")
            proxy_host = f"{proxy_parts[0]}:{proxy_parts[1]}"
            proxy_user = proxy_parts[2]
            proxy_pass = proxy_parts[3]

            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"--proxy-server=http://{proxy_host}")

            # Расширение для прокси с авторизацией
            # Для простоты используем basic auth через performance settings
            options.add_experimental_option("prefs", {
                "credentials_enable_service": False,
                "profile": {"password_manager_enabled": False}
            })

            driver = webdriver.Chrome(options=options)

            try:
                # Обработка basic auth
                driver.execute_cdp_cmd("Network.authenticate", {
                    "username": proxy_user,
                    "password": proxy_pass
                })

                driver.get("https://www.che168.com/beijing/")
                time.sleep(5)

                # Сбор данных
                elements = driver.find_elements(By.TAG_NAME, "*")
                cars = []
                for el in elements:
                    text = el.text
                    if text and len(text) > 50 and "万" in text and "年" in text:
                        img = el.find_elements(By.TAG_NAME, "img")
                        link = el.find_elements(By.TAG_NAME, "a")
                        cars.append({
                            "text": " ".join(text.split())[:300],
                            "img": img[0].get_attribute("src") if img else "",
                            "link": link[0].get_attribute("href") if link else ""
                        })
                        if len(cars) >= 20:
                            break

                print(f"  Найдено: {len(cars)}")

                for item in cars:
                    if len(all_cars) >= 10:
                        break
                    text = item["text"]
                    if len(text) < 30:
                        continue

                    price_m = re.search(r"(\d+\.?\d*)\s*万", text)
                    price = float(price_m.group(1)) * 10000 if price_m else 0

                    mileage_m = re.search(r"(\d+\.?\d*)\s*万公里", text)
                    mileage = float(mileage_m.group(1)) * 10000 if mileage_m else 0

                    year_m = re.search(r"(\d{4})-\d", text)
                    year = int(year_m.group(1)) if year_m else 0

                    if price > 0:
                        all_cars.append({
                            "title_ru": translate(text[:120]),
                            "price_cny": price,
                            "price_rub": round(price * 13, 2),
                            "mileage_km": mileage,
                            "year": year,
                            "image": item["img"],
                            "url": item["link"],
                            "proxy": proxy_host,
                        })

                print(f"  Всего: {len(all_cars)}/10")

            finally:
                driver.quit()

        except Exception as e:
            print(f"  ОШИБКА: {str(e)[:100]}")

        time.sleep(2)

    # Уникальные
    seen = set()
    unique = []
    for c in all_cars:
        key = f"{c['price_cny']}_{c['mileage_km']}_{c['year']}"
        if key not in seen and len(unique) < 10:
            seen.add(key)
            unique.append(c)

    print("\n" + "=" * 60)
    print(f"РЕЗУЛЬТАТ: {len(unique)} авто")
    print("=" * 60)

    for i, c in enumerate(unique):
        t = c["title_ru"][:60].encode("cp1251", "replace").decode("cp1251")
        print(f"[{i+1}] {t}... - {c['price_rub']:,.0f} руб")

    # Сохранение
    ts = datetime.now()
    out_json = Path(__file__).parent / "che168_selenium.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": ts.isoformat(),
            "source": "che168.com",
            "total": len(unique),
            "cars": unique
        }, f, ensure_ascii=False, indent=2)

    print(f"\nJSON: {out_json}")
    return unique

if __name__ == "__main__":
    parse_with_selenium()
