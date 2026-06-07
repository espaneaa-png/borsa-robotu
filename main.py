import json
from flask import Flask, render_template_string

app = Flask(__name__)

# Robotun ürettiği analiz verileri (Bunu senin sisteminden gelen veriye göre güncel tutuyoruz)
data_source = {
    "Analiz Sonuçları": {
        "ASELS": {
            "Güncel Fiyat": "70 TL",
            "RSI (14)": 93.75,
            "SMA Ortalaması": "67.3 TL",
            "Sinyal/Analiz": "AŞIRI ALIM (DİKKATLİ OLUNMALI)"
        },
        "EREGL": {
            "Güncel Fiyat": "43 TL",
            "RSI (14)": 0.0,
            "SMA Ortalaması": "44.41 TL",
            "Sinyal/Analiz": "AŞIRI SATIM (ALIM FIRSATI OLABİLİR)"
        },
        "THYAO": {
            "Güncel Fiyat": "315 TL",
            "RSI (14)": 81.08,
            "SMA Ortalaması": "305.3 TL",
            "Sinyal/Analiz": "AŞIRI ALIM (DİKKATLİ OLUNMALI)"
        }
    },
    "Sistem Durumu": "BIST 100 Akıllı Tarama Robotu Aktif"
}

# Web arayüzünün HTML ve CSS tasarımı (Şık Gece Modu temalı)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BIST 100 Akıllı Tarama Robotu</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121824;
            color: #e2e8f0;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            max-width: 900px;
            width: 100%;
            background: #1e293b;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            color: #38bdf8;
            margin-bottom: 5px;
        }
        .status-bar {
            text-align: center;
            font-size: 0.95rem;
            color: #34d399;
            background: rgba(52, 211, 153, 0.1);
            padding: 8px;
            border-radius: 6px;
            margin-bottom: 25px;
            font-weight: 600;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 14px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }
        th {
            background-color: #0f172a;
            color: #38bdf8;
            font-weight: 600;
        }
        tr:hover {
            background-color: #243249;
        }
        .badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85rem;
            display: inline-block;
        }
        .badge-danger {
            background-color: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid #ef4444;
        }
        .badge-success {
            background-color: rgba(34, 197, 94, 0.2);
            color: #4ade80;
            border: 1px solid #22c55e;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>📊 BIST 100 Akıllı Tarama Robotu</h1>
    <div class="status-bar">🟢 {{ data['Sistem Durumu'] }}</div>
    
    <table>
        <thead>
            <tr>
                <th>Hisse Adı</th>
                <th>Güncel Fiyat</th>
                <th>RSI (14)</th>
                <th>SMA Ortalaması</th>
                <th>Robot Sinyali / Analiz</th>
            </tr>
        </thead>
        <tbody>
            {% for hisse, detay in data['Analiz Sonuçları'].items() %}
            <tr>
                <td style="font-weight: bold; color: #f1f5f9;">{{ hisse }}</td>
                <td>{{ detay['Güncel Fiyat'] }}</td>
                <td>{{ detay['RSI (14)'] }}</td>
                <td>{{ detay['SMA Ortalaması'] }}</td>
                <td>
                    {% if 'AŞIRI ALIM' in detay['Sinyal/Analiz'] %}
                        <span class="badge badge-danger">⚠️ {{ detay['Sinyal/Analiz'] }}</span>
                    {% else %}
                        <span class="badge badge-success">✅ {{ detay['Sinyal/Analiz'] }}</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

</body>
</html>
"""

@app.route('/')
def home():
    # Sayfayı düzgün Türkçe karakterlerle ve şık tasarımla yükle
    return render_template_string(HTML_TEMPLATE, data=data_source)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)