<?php
header('Content-Type: text/html; charset=utf-8');
$json_file = __DIR__ . '/che168_cars_15.json';
if (!file_exists($json_file)) {
    die('<h1>Файл данных не найден</h1><p>Загрузите che168_cars_final.json в ту же папку</p>');
}
$data = json_decode(file_get_contents($json_file), true);
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
