"""
Выгрузка 15 автомобилей из che168.com на WordPress сайт
luchshie-yaponskie-avto.ru
"""

import json
import requests
from pathlib import Path
import http.cookiejar

# Доступы от WordPress
WP_URL = "https://luchshie-yaponskie-avto.ru"
WP_USERNAME = "administrator"
WP_PASSWORD = "*JlJ9XYu"

# Сессия с cookies
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})

def login():
    """Вход на сайт через форму"""
    login_url = f"{WP_URL}/wp-login.php"
    data = {
        "log": WP_USERNAME,
        "pwd": WP_PASSWORD,
        "wp-submit": "Войти",
        "redirect_to": f"{WP_URL}/wp-admin/",
        "testcookie": "1"
    }
    response = session.post(login_url, data=data)
    print(f"Статус входа: {response.status_code}")
    return response.status_code == 200

def get_nonce():
    """Получение nonce токена"""
    response = session.get(f"{WP_URL}/wp-admin/post-new.php")
    # Ищем nonce в странице
    import re
    match = re.search(r'"wp_rest":"([^"]+)"', response.text)
    if match:
        return match.group(1)
    # Пробуем другой паттерн
    match = re.search(r'restNonce["\']?\s*:\s*["\']?([^"\']+)["\']?', response.text)
    if match:
        return match.group(1)
    return None

def create_post(title, content, nonce, status="draft"):
    """Создание поста через REST API с cookie auth"""
    data = {
        "title": title,
        "content": content,
        "status": status,
    }
    headers = {
        "Content-Type": "application/json",
        "X-WP-Nonce": nonce
    }
    response = session.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        headers=headers,
        json=data
    )
    return response.json()

def main():
    print("=" * 60)
    print("ВЫГРУЗКА НА LUCHSHIE-YAPONSKIE-AVTO.RU")
    print("=" * 60)

    # Читаем JSON с данными
    json_file = Path(__file__).parent / "che168_cars_15.json"
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cars = data["cars"]
    print(f"\nЗагружено {len(cars)} автомобилей из {json_file}")

    # Логин
    print("\nВход на сайт...")
    if not login():
        print("[ERROR] Не удалось войти")
        return
    print("[OK] Вход выполнен")

    # Получаем nonce
    print("\nПолучение токена...")
    nonce = get_nonce()
    if not nonce:
        print("[ERROR] Не удалось получить nonce")
        # Пробуем без nonce
        nonce = ""
    else:
        print(f"[OK] Nonce получен: {nonce[:20]}...")

    # Генерируем HTML контент
    html_content = """
<style>
.car-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
.car-card { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.car-image { width: 100%; height: 200px; object-fit: cover; }
.car-info { padding: 15px; }
.car-title { font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c3e50; }
.car-price { color: #e74c3c; font-size: 18px; font-weight: bold; }
.car-details { color: #666; font-size: 14px; margin-top: 10px; }
.car-details div { margin: 5px 0; }
</style>

<h2>🚗 Автомобили из Китая (che168.com)</h2>
<p>Актуальные предложения с китайского автопортала che168.com</p>
<p><em>Цены указаны в рублях по курсу 1 CNY = 13 RUB</em></p>

<div class="car-grid">
"""

    for car in cars:
        html_content += f"""
<div class="car-card">
    <img src="{car['image']}" alt="{car['title_ru']}" class="car-image" onerror="this.style.display='none'">
    <div class="car-info">
        <div class="car-title">{car['title_ru']}</div>
        <div class="car-price">{car['price_rub']:,.0f} ₽</div>
        <div class="car-details">
            <div><b>Год:</b> {car['year']}</div>
            <div><b>Пробег:</b> {car['mileage_km']:,.0f} км</div>
            <div><b>Цена в Китае:</b> {car['price_cny']:,.0f} CNY</div>
            <div><b>Город:</b> {car['location']}</div>
        </div>
    </div>
</div>
"""

    html_content += "\n</div>\n"

    # Создаем пост
    print("\nСоздание поста...")
    title = "🇨🇳 Автомобили из Китая - 15 лотов (che168.com)"

    result = create_post(title, html_content, nonce)

    if "id" in result:
        post_id = result["id"]
        post_url = f"{WP_URL}/?p={post_id}"
        edit_url = f"{WP_URL}/wp-admin/post.php?post={post_id}&action=edit"

        print(f"\n{'='*60}")
        print("[OK] ВЫГРУЗКА УСПЕШНА!")
        print(f"{'='*60}")
        print(f"ID поста: {post_id}")
        print(f"Статус: Черновик (draft)")
        print(f"Просмотр: {post_url}")
        print(f"Редактировать: {edit_url}")
        print(f"\n{'='*60}")
        print("СПИСОК АВТОМОБИЛЕЙ:")
        print(f"{'='*60}")

        for i, car in enumerate(cars, 1):
            title_short = car['title_ru'][:60].encode('cp1251', errors='replace').decode('cp1251')
            print(f"{i}. {title_short}... — {car['price_rub']:,.0f} ₽")

        print(f"\n{'='*60}")
        print(f"Файлы:")
        print(f"  JSON: {json_file}")
        print(f"  HTML: {Path(__file__).parent / 'che168_cars_15.html'}")

    else:
        print(f"[ERROR] Ошибка создания поста: {result}")
        if "message" in result:
            print(f"Сообщение: {result['message']}")

if __name__ == "__main__":
    main()
