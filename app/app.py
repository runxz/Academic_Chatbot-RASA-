# Updated Flask App with Monitoring Dashboard
from flask import Flask, render_template, request, jsonify, render_template_string, redirect, url_for
from flask_cors import CORS
import requests
import mysql.connector
import subprocess
import psutil
import pymysql
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"
MODEL_DIR = Path("models")
LOG_FILE = "rasa_server.log"

# Database for dashboard
rasa_db = pymysql.connect(host="localhost", user="root", password="", database="rasa", charset="utf8mb4")
rasa_cursor = rasa_db.cursor()

# Chatbot database
chatbot_db = mysql.connector.connect(host="localhost", user="root", password="", database="chatbot_db")
cursor = chatbot_db.cursor()
def is_rasa_running():
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            name = proc.info['name'] or ''
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'rasa' in name or 'rasa run' in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_message = request.json["message"]
    response = requests.post(RASA_API_URL, json={"sender": "user", "message": user_message})
    if response.status_code == 200:
        rasa_reply = response.json()
        bot_response = rasa_reply[0]["text"] if rasa_reply else "Maaf, saya tidak mengerti."
    else:
        bot_response = "Maaf, ada kesalahan dalam komunikasi dengan bot."
    return jsonify({"response": bot_response})

@app.route('/monitor')
def monitor():
    model_files = sorted(MODEL_DIR.glob("*.tar.gz"), key=lambda f: f.stat().st_mtime, reverse=True)
    last_model = model_files[0].name if model_files else "No model found"
    last_updated = datetime.fromtimestamp(model_files[0].stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S") if model_files else "N/A"
    log_content = Path(LOG_FILE).read_text(encoding="utf-8")[-3000:] if Path(LOG_FILE).exists() else "Log not found."
 
    is_running = is_rasa_running()

    rasa_cursor.execute("SELECT data FROM events WHERE type_name = 'user'")
    fallback_count, total_count, confidence_sum = 0, 0, 0.0
    for (data_json,) in rasa_cursor.fetchall():
        try:
            data = json.loads(data_json)
            intent = data.get("parse_data", {}).get("intent", {})
            confidence = intent.get("confidence", 1.0)
            intent_name = intent.get("name", "")
            total_count += 1
            confidence_sum += confidence
            if intent_name == "nlu_fallback":
                fallback_count += 1
        except:
            continue
    fallback_rate = round((fallback_count / total_count) * 100, 2) if total_count else 0
    avg_confidence = round((confidence_sum / total_count), 2) if total_count else 0

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rasa Monitoring</title>
        <style>
            body { font-family: Arial; background: #f0f0f0; padding: 20px; }
            .box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); max-width: 800px; margin: auto; }
            .status { font-weight: bold; color: white; padding: 5px 10px; border-radius: 5px; display: inline-block; }
            .running { background-color: #28a745; }
            .stopped { background-color: #dc3545; }
            button { padding: 10px 20px; font-size: 16px; border-radius: 6px; border: none; background: #007BFF; color: white; cursor: pointer; }
            button:hover { background: #0056b3; }
            pre { background: #222; color: #0f0; padding: 10px; border-radius: 5px; overflow: auto; max-height: 300px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🤖 Rasa Monitoring Dashboard</h1>
            <p><b>Status:</b> <span class="status {{ 'running' if is_running else 'stopped' }}">{{ 'Running' if is_running else 'Not Running' }}</span></p>
            <p><b>Last model:</b> {{ last_model }}</p>
            <p><b>Last updated:</b> {{ last_updated }}</p>
            <p><b>Fallback rate:</b> {{ fallback_rate }}%</p>
            <p><b>Avg NLU confidence:</b> {{ avg_confidence }}</p>
            <form method="POST" action="/monitor/train">
                <button type="submit">Retrain and Reload Model</button>
            </form>
            <h2>Server Log:</h2>
            <pre>{{ log_content }}</pre>
        </div>
    </body>
    </html>
    """
    return render_template_string(template, last_model=last_model, last_updated=last_updated,
                                  fallback_rate=fallback_rate, avg_confidence=avg_confidence,
                                  is_running=is_running, log_content=log_content)

@app.route("/monitor/train", methods=["POST"])
def train_rasa():
    subprocess.Popen(["python", "app/train_and_reload.py"])
    return redirect(url_for("monitor"))

# Existing endpoints (kategori_intent, informasi, wikipedia)... unchanged

# Endpoint untuk mendapatkan semua kategori intent
@app.route('/kategori_intent', methods=['GET'])
def get_kategori():
    cursor.execute("SELECT * FROM kategori_intent")
    result = cursor.fetchall()
    data = [{"id": row[0], "nama_kategori": row[1]} for row in result]
    return jsonify(data)

# Endpoint untuk menambahkan kategori intent
@app.route('/kategori_intent', methods=['POST'])
def add_kategori():
    data = request.get_json()
    cursor.execute("INSERT INTO kategori_intent (nama_kategori) VALUES (%s)", (data['nama_kategori'],))
    db.commit()
    return jsonify({"message": "Kategori berhasil ditambahkan"}), 201

# Endpoint untuk mendapatkan semua informasi berdasarkan kategori
@app.route('/informasi/<int:kategori_id>', methods=['GET'])
def get_informasi(kategori_id):
    cursor.execute("SELECT * FROM informasi WHERE kategori_id = %s", (kategori_id,))
    result = cursor.fetchall()
    data = [{"id": row[0], "kategori_id": row[1], "judul": row[2], "deskripsi": row[3]} for row in result]
    return jsonify(data)

# Endpoint untuk menambahkan informasi baru
@app.route('/informasi', methods=['POST'])
def add_informasi():
    data = request.get_json()
    cursor.execute("INSERT INTO informasi (kategori_id, judul, deskripsi) VALUES (%s, %s, %s)", 
                   (data['kategori_id'], data['judul'], data['deskripsi']))
    db.commit()
    return jsonify({"message": "Informasi berhasil ditambahkan"}), 201

# Endpoint untuk mengupdate informasi
@app.route('/informasi/<int:id>', methods=['PUT'])
def update_informasi(id):
    data = request.get_json()
    cursor.execute("UPDATE informasi SET judul = %s, deskripsi = %s WHERE id = %s", 
                   (data['judul'], data['deskripsi'], id))
    db.commit()
    return jsonify({"message": "Informasi berhasil diperbarui"})

# Endpoint untuk menghapus informasi
@app.route('/informasi/<int:id>', methods=['DELETE'])
def delete_informasi(id):
    cursor.execute("DELETE FROM informasi WHERE id = %s", (id,))
    db.commit()
    return jsonify({"message": "Informasi berhasil dihapus"})

def search_wikipedia(query):
    """Search Wikipedia for the best matching page title"""
    search_url = "https://id.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        search_results = response.json()
        if "query" in search_results and "search" in search_results["query"]:
            search_hits = search_results["query"]["search"]
            if search_hits:
                return search_hits[0]["title"]  # Return the first matching title
    return None

@app.route("/search_wikipedia", methods=["GET"])
def get_wikipedia_info():
    query = request.args.get("query")  # Get query from request
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    # Step 1: Find the best Wikipedia page title
    best_title = search_wikipedia(query=query)  # ✅ Fixed issue here
    if not best_title:
        return jsonify({"error": "No Wikipedia page found"}), 404

    # Step 2: Get Wikipedia summary of the best match
    summary_url = f"https://id.wikipedia.org/api/rest_v1/page/summary/{best_title.replace(' ', '_')}"
    response = requests.get(summary_url)

    if response.status_code == 200:
        data = response.json()
        return jsonify({
            "title": data.get("title", "Tidak diketahui"),
            "extract": data.get("extract", "Tidak ada ringkasan tersedia."),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
        })
    else:
        return jsonify({"error": "Wikipedia summary request failed"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
