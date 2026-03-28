#!/usr/bin/env python3
"""
Che168 parser for GitHub Actions
Uses HTTP connection through proxy (che168 may block HTTPS)
"""
import json, socket, base64, re, time
from datetime import datetime

PROXY_HOST = "170.83.237.197"
PROXY_PORT = 8000
PROXY_USER = "12QaFM"
PROXY_PASS = "Dv60es"

# Пробуем HTTP вместо HTTPS
TARGET_HOST = "www.che168.com"
TARGET_PORT = 80

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def create_proxy_connection():
    """Create connection through proxy with proper CONNECT"""
    auth = base64.b64encode(f"{PROXY_USER}:{PROXY_PASS}".encode()).decode()

    sock = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=30)
    connect_request = f"CONNECT {TARGET_HOST}:{TARGET_PORT} HTTP/1.0\r\nProxy-Authorization: Basic {auth}\r\n\r\n"
    sock.send(connect_request.encode())

    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            raise Exception("Proxy connection closed")
        response += chunk

    response_str = response.decode('utf-8', errors='ignore')
    if "200" not in response_str.split("\r\n")[0]:
        raise Exception(f"Proxy error: {response_str[:200]}")

    return sock

def parse():
    """Parse che168.com through proxy"""
    cars = []
    results = []
    debug_html = ""
    result = {"proxy": f"{PROXY_HOST}:{PROXY_PORT}", "url": f"http://{TARGET_HOST}/beijing/", "status": "error", "error": ""}

    try:
        sock = create_proxy_connection()

        # Отправляем HTTP запрос (без SSL)
        request = f"GET /beijing/ HTTP/1.1\r\nHost: {TARGET_HOST}\r\n"
        for key, value in HEADERS.items():
            request += f"{key}: {value}\r\n"
        request += "Connection: close\r\n\r\n"

        sock.send(request.encode())

        # Читаем ответ
        response = b""
        sock.settimeout(30)
        while True:
            try:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break

        sock.close()

        # Разбираем HTTP заголовки
        header_end = response.find(b"\r\n\r\n")
        headers = response[:header_end].decode('utf-8', errors='ignore')
        body_bytes = response[header_end + 4:]

        # Определяем кодировку из заголовков или мета-тега
        charset = 'gb2312'  # По умолчанию для che168
        if 'charset=gbk' in headers.lower() or 'charset=gb2312' in headers.lower():
            charset = 'gbk'

        # Пробуем декодировать
        try:
            body = body_bytes.decode(charset, errors='ignore')
        except:
            body = body_bytes.decode('utf-8', errors='ignore')

        debug_html = body[:50000]

        # Ищем цены в разных форматах
        prices = []
        # Формат: X.XX 万
        prices.extend(re.findall(r'(\d+\.?\d*)\s*万', body))
        # Формат: ¥XXX 或 ￥XXX
        prices.extend(re.findall(r'￥?\s*(\d+\.?\d*)\s*万', body))

        for p in prices[:10]:
            price_cny = float(p) * 10000
            cars.append({
                "price_cny": price_cny,
                "price_rub": round(price_cny * 13, 2)
            })

        if cars:
            result["status"] = "success"
        elif "404" in response_str[:500]:
            result["error"] = "404 Not Found - URL may be invalid"
        elif "403" in response_str[:500]:
            result["error"] = "403 Forbidden - blocked by anti-bot"
        else:
            result["error"] = "No prices found in HTML"

    except Exception as e:
        result["error"] = str(e)[:200]

    results.append(result)

    return cars, results, debug_html

if __name__ == "__main__":
    cars, results, debug_html = parse()
    print(f"Found: {len(cars)} cars")

    output = {
        "timestamp": datetime.now().isoformat(),
        "source": "che168.com",
        "proxies_tested": 1,
        "cars_found": len(cars),
        "results": results,
        "cars": cars
    }

    with open("che168_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    if debug_html:
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(debug_html)
        print("Debug HTML saved to debug_page.html")
