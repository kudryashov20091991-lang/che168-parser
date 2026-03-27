"""
Быстрый парсер che168.com - requests + BeautifulSoup
"""
import requests
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

ZH_RU_DICT = {
    "万公里": " тыс. км",
    "年": " г.",
    "北京": "Пекин",
    "奔驰": "Mercedes-Benz",
    "宝马": "BMW",
    "奥迪": "Audi",
    "保时捷": "Porsche",
    "路虎": "Land Rover",
    "揽胜": "Range Rover",
    "Model Y": "Tesla Model Y",
}

def translate(text):
    for zh, ru in ZH_RU_DICT.items():
        text = text.replace(zh, ru)
    return text

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

print("Загрузка страницы...")
resp = requests.get("https://www.che168.com/beijing/", headers=headers, timeout=30)
resp.encoding = 'gb2312'
html = resp.text

print("Парсинг...")
soup = BeautifulSoup(html, 'html.parser')

cars = []
# Ищем элементы с классами содержащими 'car' или 'vehicle'
for el in soup.select('[class*="car"], [class*="vehicle"], li, a[href*="/dealer/"]'):
    text = el.get_text(strip=True)
    if len(text) > 50 and '万' in text and len(cars) < 15:
        # Извлекаем цену
        price_match = re.search(r'(\d+\.?\d*)\s*万', text)
        price_cny = float(price_match.group(1)) * 10000 if price_match else 0

        # Извлекаем пробег
        mileage_match = re.search(r'(\d+\.?\d*)\s*万公里', text)
        mileage = float(mileage_match.group(1)) * 10000 if mileage_match else 0

        # Извлекаем год
        year_match = re.search(r'(\d{4})-\d', text)
        year = int(year_match.group(1)) if year_match else 0

        # Извлекаем картинку
        img = el.find('img')
        img_src = img['src'] if img and img.get('src') else ''

        # Извлекаем ссылку
        link = el.find('a')
        url = link['href'] if link and link.get('href') else ''

        if price_cny > 0:
            title_ru = translate(text[:150])
            cars.append({
                "title_ru": title_ru,
                "price_cny": price_cny,
                "price_rub": round(price_cny * 13, 2),
                "mileage_km": mileage,
                "year": year,
                "image": img_src,
                "url": url if url.startswith('http') else f'https://www.che168.com{url}',
            })

print(f"Найдено авто: {len(cars)}")

# Сохраняем JSON
output = Path(__file__).parent / "che168_cars_new.json"
with open(output, "w", encoding="utf-8") as f:
    json.dump({"timestamp": datetime.now().isoformat(), "cars": cars}, f, ensure_ascii=False, indent=2)

# Генерируем HTML
html_out = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Авто из Китая</title>
    <style>
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }}
        .img {{ width: 100%; height: 200px; object-fit: cover; }}
        .info {{ padding: 15px; }}
        .price {{ color: #e74c3c; font-size: 18px; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Автомобили из Китая (che168.com)</h1>
    <p>Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")}</p>
    <div class="grid">
"""
for c in cars:
    html_out += f"""
        <div class="card">
            <img src="{c['image']}" onerror="this.src='https://via.placeholder.com/400x200'" class="img">
            <div class="info">
                <div style="font-weight:bold;margin-bottom:10px">{c['title_ru'][:100]}</div>
                <div class="price">{c['price_rub']:,.0f} ₽</div>
                <div style="color:#666;font-size:14px;margin-top:10px">
                    <div>Год: {c['year']}</div>
                    <div>Пробег: {c['mileage_km']:,.0f} км</div>
                    <div>Цена: {c['price_cny']:,.0f} CNY</div>
                </div>
            </div>
        </div>
"""
html_out += """
    </div>
</body>
</html>
"""

html_file = Path(__file__).parent / "che168_cars_new.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_out)

print(f"JSON: {output}")
print(f"HTML: {html_file}")
print("ГОТОВО!")
