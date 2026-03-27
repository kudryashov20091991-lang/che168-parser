<?php
/**
 * che168.com парсер через PHP cURL + прокси
 * Запускать на Beget: php che168_parser.php
 */

$proxies = [
    "45.32.56.105:13851",
    "45.32.56.105:13852",
    "45.32.56.105:13853",
];
$proxy_auth = "Ek0G8F:GR0Fhj";

$cars = [];

foreach ($proxies as $i => $proxy) {
    if (count($cars) >= 10) break;

    echo "[".($i+1)] Прокси: $proxy\n";

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://www.che168.com/beijing/");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_PROXY, $proxy);
    curl_setopt($ch, CURLOPT_PROXYUSERPWD, $proxy_auth);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

    $html = curl_exec($ch);
    $error = curl_error($ch);
    curl_close($ch);

    if ($error) {
        echo "  Ошибка: $error\n";
        continue;
    }

    echo "  Страница загружена (".strlen($html)." байт)\n";

    // Парсинг цен
    if (preg_match_all('/(\d+\.?\d*)\s*万/', $html, $matches)) {
        foreach ($matches[1] as $price) {
            $price_cny = floatval($price) * 10000;
            if ($price_cny > 10000 && count($cars) < 10) {
                $cars[] = [
                    'price_cny' => $price_cny,
                    'price_rub' => round($price_cny * 13, 2),
                    'proxy' => $proxy
                ];
                echo "  Авто: {$price_cny} CNY\n";
            }
        }
    }

    sleep(2);
}

echo "\nИтого: ".count($cars)." авто\n";

// Сохранение
file_put_contents('che168_cars.json', json_encode([
    'timestamp' => date('c'),
    'total' => count($cars),
    'cars' => $cars
], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

echo "Сохранено в che168_cars.json\n";
?>
