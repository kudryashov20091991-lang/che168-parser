<?php
/**
 * che168.com - Парсер автомобилей через прокси
 * Запуск на Beget: просто открыть в браузере https://ahilesor.beget.ru/che168_beget_final.php
 *
 * Прокси: 45.32.56.105:13851/52/53
 * Auth: Ek0G8F:GR0Fhj
 */

set_time_limit(120);
ignore_user_abort(true);

$proxies = [
    ['host' => '45.32.56.105', 'port' => '13851'],
    ['host' => '45.32.56.105', 'port' => '13852'],
    ['host' => '45.32.56.105', 'port' => '13853'],
];
$proxy_auth = 'Ek0G8F:GR0Fhj';
$user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';

$cars = [];
$results = [];

echo "<h1>Парсинг che168.com через прокси</h1>";
echo "<p>Запуск: " . date('Y-m-d H:i:s') . "</p>";
echo "<hr>";

foreach ($proxies as $i => $proxy) {
    if (count($cars) >= 10) break;

    $proxy_str = $proxy['host'] . ':' . $proxy['port'];
    echo "<p><strong>[Попытка " . ($i+1) . "]</strong> Прокси: $proxy_str</p>";

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, 'https://www.che168.com/beijing/');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_PROXY, $proxy_str);
    curl_setopt($ch, CURLOPT_PROXYUSERPWD, $proxy_auth);
    curl_setopt($ch, CURLOPT_PROXYTYPE, CURLPROXY_HTTP);
    curl_setopt($ch, CURLOPT_TIMEOUT, 25);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 8);
    curl_setopt($ch, CURLOPT_USERAGENT, $user_agent);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Accept: text/html,application/xhtml+xml',
        'Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8',
    ]);

    $html = curl_exec($ch);
    $error = curl_error($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($error) {
        echo "<p style='color:red'>Ошибка: $error</p>";
        $results[] = ['proxy' => $proxy_str, 'status' => 'error', 'error' => $error];
        continue;
    }

    echo "<p style='color:green'>HTTP: $http_code, Размер: " . strlen($html) . " байт</p>";

    // Проверка IP через этот же прокси
    $ch_ip = curl_init();
    curl_setopt($ch_ip, CURLOPT_URL, 'https://api.ipify.org/');
    curl_setopt($ch_ip, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch_ip, CURLOPT_PROXY, $proxy_str);
    curl_setopt($ch_ip, CURLOPT_PROXYUSERPWD, $proxy_auth);
    curl_setopt($ch_ip, CURLOPT_TIMEOUT, 10);
    $ip = curl_exec($ch_ip);
    curl_close($ch_ip);
    echo "<p>IP прокси: " . ($ip ?: 'не определен') . "</p>";

    // Парсинг данных
    if (strlen($html) > 1000) {
        // Ищем цены в формате XXX万
        preg_match_all('/(\d+\.?\d*)\s*万/', $html, $price_matches);

        foreach ($price_matches[1] as $price) {
            $price_cny = floatval($price) * 10000;
            if ($price_cny > 50000 && count($cars) < 10) {
                $cars[] = [
                    'price_cny' => $price_cny,
                    'price_rub' => round($price_cny * 13, 2),
                    'proxy' => $proxy_str,
                ];
                echo "<p style='color:blue'>Найдено авто: " . number_format($price_cny, 0, '.', ' ') . " CNY (~" . number_format($price_cny * 13, 0, '.', ' ') . " ₽)</p>";
            }
        }

        // Ищем названия авто (китайские иероглифы + цифры)
        preg_match_all('/[\x{4e00}-\x{9fff}]{2,10}\d{4}[\x{4e00}-\x{9fff}]{1,5}/u', $html, $title_matches);
        if (!empty($title_matches[0])) {
            echo "<p>Найдено заголовков: " . count($title_matches[0]) . "</p>";
        }
    }

    $results[] = ['proxy' => $proxy_str, 'status' => 'ok', 'http' => $http_code, 'size' => strlen($html)];
    sleep(2);
}

echo "<hr>";
echo "<h2>ИТОГО: " . count($cars) . " автомобилей</h2>";

// Сохранение JSON
$output = [
    'timestamp' => date('c'),
    'source' => 'che168.com',
    'proxies_tested' => count($results),
    'cars_found' => count($cars),
    'results' => $results,
    'cars' => $cars,
];

$json_file = __DIR__ . '/che168_result.json';
file_put_contents($json_file, json_encode($output, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
echo "<p>Сохранено: $json_file</p>";

// HTML отчет
echo "<h2>Детали:</h2><pre>" . json_encode($results, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . "</pre>";
echo "<h2>Автомобили:</h2><pre>" . json_encode($cars, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . "</pre>";

?>
