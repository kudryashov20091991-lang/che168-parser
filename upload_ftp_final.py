"""
Выгрузка на luchshie-yaponskie-avto.ru через FTP
"""
import ftplib
from pathlib import Path
from datetime import datetime

FTP_HOST = 'luchshie-yaponskie-avto.ru'
FTP_USER = 'luchshie-yaponskie-avto_ru_turbo'
FTP_PASS = 'Qwerty123456'
FTP_PATH = '/luchshie-yaponskie-avto.ru/public_html/'

FILES_TO_UPLOAD = [
    'che168_cars_final.json',
    'che168_cars_final.html',
]

print("Подключение к FTP...")
ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
print(f"Успешно подключено к {FTP_HOST}")

for filename in FILES_TO_UPLOAD:
    filepath = Path(__file__).parent / filename
    if filepath.exists():
        print(f"Загрузка {filename}...")
        with open(filepath, 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f)
        print(f"  ✓ {filename} загружен")
    else:
        print(f"  ✗ {filename} не найден")

# Создаем index.php для просмотра
index_php = """<?php
header('Content-Type: text/html; charset=utf-8');
$data = json_decode(file_get_contents('che168_cars_final.json'), true);
$cars = $data['cars'] ?? [];
?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Авто из Китая - che168.com</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .img { width: 100%; height: 200px; object-fit: cover; background: #eee; }
        .info { padding: 15px; }
        .title { font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #222; }
        .price { color: #e74c3c; font-size: 20px; font-weight: bold; margin: 10px 0; }
        .details { color: #666; font-size: 14px; line-height: 1.6; }
        .meta { color: #999; font-size: 12px; margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <h1>🚗 Автомобили из Китая (che168.com)</h1>
    <p>Парсинг выполнен: <?= date('d.m.Y H:i') ?> | Всего авто: <?= count($cars) ?></p>

    <div class="grid">
        <?php foreach ($cars as $car): ?>
        <div class="card">
            <img src="<?= htmlspecialchars($car['image'] ?: 'https://via.placeholder.com/400x200?text=No+Image') ?>"
                 class="img" onerror="this.src='https://via.placeholder.com/400x200?text=No+Image'">
            <div class="info">
                <div class="title"><?= htmlspecialchars(mb_substr($car['title_ru'], 0, 100)) ?></div>
                <div class="price"><?= number_format($car['price_rub']) ?> ₽</div>
                <div class="details">
                    <div>📅 Год: <?= $car['year'] ?></div>
                    <div>🛣️ Пробег: <?= number_format($car['mileage_km']) ?> км</div>
                    <div>💰 Цена в Китае: <?= number_format($car['price_cny']) ?> CNY</div>
                </div>
                <div class="meta">
                    <div>Источник: che168.com</div>
                    <div>Город: <?= $car['location'] ?? 'Китай' ?></div>
                </div>
            </div>
        </div>
        <?php endforeach; ?>
    </div>
</body>
</html>
"""

php_path = Path(__file__).parent / 'china_cars.php'
with open(php_path, 'w', encoding='utf-8') as f:
    f.write(index_php)

print(f"Загрузка china_cars.php...")
with open(php_path, 'rb') as f:
    ftp.storbinary('STOR china_cars.php', f)
print("  ✓ china_cars.php загружен")

ftp.quit()
print("\n✓ ВСЕ ФАЙЛЫ ЗАГРУЖЕНЫ НА FTP!")
print(f"Ссылка: http://luchshie-yaponskie-avto.ru/china_cars.php")
