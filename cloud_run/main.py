#!/usr/bin/env python3
"""
Парсер Che168 для Google Cloud Run
Запуск по HTTP запросу
"""

import requests
import re
import json
import time
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

PROXIES = [
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13851', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13851'},
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13852', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13852'},
    {'http': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13853', 'https': 'http://Ek0G8F:GR0Fhj@45.32.56.105:13853'},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

def parse_che168():
    cars = []
    results = []

    for i, proxy in enumerate(PROXIES):
        if len(cars) >= 10:
            break

        proxy_label = proxy['http'].split('@')[1]

        try:
            ip_resp = requests.get('https://api.ipify.org/', proxies=proxy, headers=HEADERS, timeout=15)

            resp = requests.get('https://www.che168.com/beijing/', proxies=proxy, headers=HEADERS, timeout=30)

            if resp.status_code == 200 and len(resp.text) > 1000:
                html = resp.text
                prices = re.findall(r'(\d+\.?\d*)\s*万', html)
                for price in prices:
                    price_cny = float(price) * 10000
                    if price_cny > 50000 and len(cars) < 10:
                        cars.append({
                            'price_cny': price_cny,
                            'price_rub': round(price_cny * 13, 2),
                            'proxy': proxy_label,
                        })

                results.append({'proxy': proxy_label, 'status': 'ok', 'size': len(resp.text)})
            else:
                results.append({'proxy': proxy_label, 'status': 'error', 'http': resp.status_code})

        except Exception as e:
            results.append({'proxy': proxy_label, 'status': 'error', 'error': str(e)[:100]})

        time.sleep(1)

    return {'results': results, 'cars': cars}

@app.route('/')
def index():
    return jsonify({
        'status': 'ready',
        'endpoint': '/parse'
    })

@app.route('/parse')
def parse():
    data = parse_che168()

    output = {
        'timestamp': datetime.now().isoformat(),
        'source': 'che168.com',
        'proxies_tested': len(data['results']),
        'cars_found': len(data['cars']),
        'results': data['results'],
        'cars': data['cars'],
    }

    return jsonify(output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
