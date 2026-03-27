"""
Парсер dongchedi.com с ротацией прокси
Каждый запрос идет через новый прокси
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
from pathlib import Path

# Прокси для ротации (формат: host:port:username:password)
PROXIES = [
    {"host": "45.32.56.105", "port": "13853", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"host": "45.32.56.105", "port": "13852", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"host": "45.32.56.105", "port": "13851", "username": "Ek0G8F", "password": "GR0Fhj"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.dongchedi.com/",
}

def get_proxy_url(proxy_info):
    """Формирует URL прокси для requests"""
    return f"http://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"

def get_proxy_dict(proxy_info):
    """Возвращает словарь прокси для requests"""
    proxy_url = get_proxy_url(proxy_info)
    return {
        "http": proxy_url,
        "https": proxy_url,
    }

def check_proxy_ip(proxy_info):
    """Проверяет IP через прокси"""
    try:
        proxies = get_proxy_dict(proxy_info)
        response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=15)
        if response.status_code == 200:
            return response.json().get("ip")
    except Exception as e:
        return f"Error: {e}"
    return None

def parse_dongchedi(url, proxy_info):
    """Парсит страницу dongchedi через указанный прокси"""
    result = {
        "url": url,
        "proxy": f"{proxy_info['host']}:{proxy_info['port']}",
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "data": None,
        "error": None,
    }

    try:
        proxies = get_proxy_dict(proxy_info)
        response = requests.get(url, headers=HEADERS, proxies=proxies, timeout=30)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")

        # Извлекаем данные
        car_data = {
            "title": "",
            "price": "",
            "year": "",
            "mileage": "",
            "engine": "",
            "transmission": "",
            "location": "",
        }

        # Заголовок
        title_tag = soup.find("h1") or soup.find("title")
        if title_tag:
            car_data["title"] = title_tag.get_text(strip=True)[:200]

        # Цена
        price_elem = soup.find(string=lambda t: t and "万" in t and any(c.isdigit() for c in t))
        if price_elem:
            car_data["price"] = price_elem.strip()[:50]

        # Ищем данные в JSON-LD или script тегах
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get("name"):
                        car_data["title"] = data["name"]
                    if data.get("offers") and data["offers"].get("price"):
                        car_data["price"] = str(data["offers"]["price"])
            except:
                pass

        # Ищем в __NEXT_DATA__
        next_data = soup.find("script", id="__NEXT_DATA__")
        if next_data:
            try:
                data = json.loads(next_data.string)
                props = data.get("props", {}).get("pageProps", {})
                if props:
                    car_data["title"] = props.get("title", car_data["title"])
                    car_data["price"] = str(props.get("price", props.get("minPrice", "")))
            except:
                pass

        result["data"] = car_data
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)

    return result

def main():
    """Тестовый парсинг 15 лотов с ротацией прокси"""
    print("=" * 60)
    print("ПАРСИНГ DONGCHEDI.COM С РОТАЦИЕЙ ПРОКСИ")
    print("=" * 60)

    # Проверяем прокси
    print("\n[1] Проверка прокси...")
    for i, proxy in enumerate(PROXIES):
        ip = check_proxy_ip(proxy)
        print(f"  Прокси #{i+1} ({proxy['host']}:{proxy['port']}): IP = {ip}")

    # Тестовые URL (замени на реальные URL с dongchedi)
    # Для теста используем 15 URL
    test_urls = [
        "https://www.dongchedi.com/",  # Замени на реальные URL лотов
    ] * 15

    print(f"\n[2] Парсинг 15 лотов (каждые 3 минуты, ротация прокси)...")

    results = []
    proxy_index = 0

    for i, url in enumerate(test_urls):
        proxy = PROXIES[proxy_index % len(PROXIES)]
        print(f"\n[{i+1}/15] URL: {url}")
        print(f"       Прокси: {proxy['host']}:{proxy['port']}")

        result = parse_dongchedi(url, proxy)
        results.append(result)

        if result["success"]:
            print(f"       Статус: OK - {result['data']['title'][:50] if result['data']['title'] else 'N/A'}")
        else:
            print(f"       Статус: ERROR - {result['error']}")

        # Ротация прокси
        proxy_index += 1

        # Ждем 3 минуты перед следующим запросом (для теста 10 секунд)
        if i < len(test_urls) - 1:
            wait_time = 10  # Для теста. В продакшене: 180 (3 минуты)
            print(f"       Ожидание {wait_time} сек...")
            time.sleep(wait_time)

    # Сохраняем результаты
    output_file = Path(__file__).parent / "dongchedi_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[3] Результаты сохранены в: {output_file}")

    # Статистика
    success_count = sum(1 for r in results if r["success"])
    print(f"\n[4] Итого: {success_count}/{len(results)} успешных")

    return results

if __name__ == "__main__":
    main()
