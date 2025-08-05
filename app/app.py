# app/app.py

from flask import Flask, render_template, request, jsonify, render_template_string, redirect, url_for
from flask_cors import CORS
import requests
import mysql.connector
import subprocess
import psutil
import pymysql
import yaml
import json
import os
import google.generativeai as genai
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}

GEMINI_API_KEY = "AIzaSyDstqBL7mgv2smascyPJzfqCf7u6iHooNQ"  # gunakan dari Google AI Studio
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CORS(app)

RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"
MODEL_DIR = Path("models")
LOG_FILE = "rasa_server.log"

# DB connections
rasa_db = pymysql.connect(host="localhost", user="root", password="admin123", database="rasa", charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
rasa_cursor = rasa_db.cursor()

chatbot_db = mysql.connector.connect(host="localhost", user="root", password="admin123", database="chatbot_db")
cursor = chatbot_db.cursor()

def connect_db():
    return chatbot_db

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    # gunakan endpoint /model/parse untuk mendapatkan intent
    parse_response = requests.post("http://localhost:5005/model/parse", json={"text": user_message})
    
    if parse_response.status_code == 200:
        parsed = parse_response.json()
        intent = parsed.get("intent", {}).get("name", "unknown")
        confidence = parsed.get("intent", {}).get("confidence", 0)

        # Debug intent
        print(f"[DEBUG] Intent: {intent}, Confidence: {confidence}")

        # kirim ke /webhooks/rest/webhook hanya jika bukan fallback
        if intent == "nlu_fallback":
            gemini_resp = requests.post("http://localhost:5000/fallback_gemini", json={"message": user_message})
            gemini_text = gemini_resp.json().get("response", "Maaf, tidak bisa menjawab.")
            return jsonify({"response": gemini_text, "intent": intent, "confidence": confidence})
        else:
            rasa_reply = requests.post(RASA_API_URL, json={"sender": "user", "message": user_message})
            bot_response = rasa_reply.json()[0]["text"] if rasa_reply.ok and rasa_reply.json() else "Maaf, tidak mengerti."
            return jsonify({"response": bot_response, "intent": intent, "confidence": confidence})
    else:
        return jsonify({"response": "Gagal mendapatkan intent", "intent": None, "confidence": 0})


@app.route("/admin", methods=["GET"])
def admin_panel():
    conn = connect_db()
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM files ORDER BY id DESC")
        files = cur.fetchall()
        cur.execute("SELECT * FROM kategori_intent ORDER BY id DESC")
        kategori = cur.fetchall()
    return render_template("admin_form.html", files=files, kategori=kategori)

@app.route("/admin/upload_file", methods=["POST"])
def upload_file():
    nama = request.form["nama"]
    tahun = request.form["tahun"]
    deskripsi = request.form["deskripsi"]
    file = request.files["file"]

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        link = f"/static/uploads/{filename}"

        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO files (nama, tahun, deskripsi, link) VALUES (%s, %s, %s, %s)",
                        (nama, tahun, deskripsi, link))
        conn.commit()
        return redirect("/admin")
    return "File tidak valid", 400

@app.route("/admin/delete_file/<int:file_id>", methods=["POST"])
def delete_file(file_id):
    conn = connect_db()
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT link FROM files WHERE id = %s", (file_id,))
        result = cur.fetchone()
        if result:
            file_path = result["link"].lstrip("/")
            if os.path.exists(file_path):
                os.remove(file_path)
        cur.execute("DELETE FROM files WHERE id = %s", (file_id,))
    conn.commit()
    return redirect("/admin")

@app.route("/admin/kategori", methods=["POST"])
def admin_add_kategori():
    nama_intent = request.form["nama_intent"]
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO kategori_intent (nama_intent) VALUES (%s)", (nama_intent,))
    conn.commit()
    return redirect("/admin")

@app.route("/admin/intent", methods=["POST"])
def add_intent():
    intent_name = request.form["intent"]
    examples = request.form["examples"].strip().split("\n")

    with open("data/nlu.yml", "r", encoding="utf-8") as f:
        nlu_data = yaml.safe_load(f)

    nlu_data["nlu"].append({
        "intent": intent_name,
        "examples": "|\n" + "\n".join([f"  - {e.strip()}" for e in examples])
    })

    with open("data/nlu.yml", "w", encoding="utf-8") as f:
        yaml.dump(nlu_data, f, allow_unicode=True)

    return redirect("/admin")

@app.route("/monitor")
def monitor():
    model_files = sorted(MODEL_DIR.glob("*.tar.gz"), key=lambda f: f.stat().st_mtime, reverse=True)
    last_model = model_files[0].name if model_files else "No model found"
    last_updated = datetime.fromtimestamp(model_files[0].stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S") if model_files else "N/A"
    log_content = Path(LOG_FILE).read_text(encoding="utf-8")[-3000:] if Path(LOG_FILE).exists() else "Log not found."
    is_running = is_rasa_running()

    rasa_cursor.execute("SELECT data FROM events WHERE type_name = 'user'")
    fallback_count, total_count, confidence_sum = 0, 0, 0.0
    for row in rasa_cursor.fetchall():
        try:
            data = json.loads(row["data"])
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

    return render_template("monitor.html")

@app.route("/monitor/train", methods=["POST"])
def train_rasa():
    subprocess.Popen(["python", "app/train_and_reload.py"])
    return redirect(url_for("monitor"))

@app.route('/kategori_intent', methods=['GET'])
def get_kategori():
    cursor.execute("SELECT * FROM kategori_intent")
    result = cursor.fetchall()
    data = [{"id": row[0], "nama_kategori": row[1]} for row in result]
    return jsonify(data)

@app.route('/kategori_intent', methods=['POST'])
def api_add_kategori():
    data = request.get_json()
    cursor.execute("INSERT INTO kategori_intent (nama_kategori) VALUES (%s)", (data['nama_kategori'],))
    chatbot_db.commit()
    return jsonify({"message": "Kategori berhasil ditambahkan"}), 201

@app.route('/informasi/<int:kategori_id>', methods=['GET'])
def get_informasi(kategori_id):
    cursor.execute("SELECT * FROM informasi WHERE kategori_id = %s", (kategori_id,))
    result = cursor.fetchall()
    data = [{"id": row[0], "kategori_id": row[1], "judul": row[2], "deskripsi": row[3]} for row in result]
    return jsonify(data)

@app.route('/informasi', methods=['POST'])
def add_informasi():
    data = request.get_json()
    cursor.execute("INSERT INTO informasi (kategori_id, judul, deskripsi) VALUES (%s, %s, %s)",
                   (data['kategori_id'], data['judul'], data['deskripsi']))
    chatbot_db.commit()
    return jsonify({"message": "Informasi berhasil ditambahkan"}), 201

@app.route('/informasi/<int:id>', methods=['PUT'])
def update_informasi(id):
    data = request.get_json()
    cursor.execute("UPDATE informasi SET judul = %s, deskripsi = %s WHERE id = %s",
                   (data['judul'], data['deskripsi'], id))
    chatbot_db.commit()
    return jsonify({"message": "Informasi berhasil diperbarui"})

@app.route('/informasi/<int:id>', methods=['DELETE'])
def delete_informasi(id):
    cursor.execute("DELETE FROM informasi WHERE id = %s", (id,))
    chatbot_db.commit()
    return jsonify({"message": "Informasi berhasil dihapus"})

def search_wikipedia(query):
    response = requests.get("https://id.wikipedia.org/w/api.php", params={
        "action": "query", "format": "json", "list": "search", "srsearch": query
    })
    if response.ok:
        results = response.json().get("query", {}).get("search", [])
        return results[0]["title"] if results else None
    return None

@app.route("/search_wikipedia", methods=["GET"])
def get_wikipedia_info():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    best_title = search_wikipedia(query)
    if not best_title:
        return jsonify({"error": "No Wikipedia page found"}), 404

    summary_url = f"https://id.wikipedia.org/api/rest_v1/page/summary/{best_title.replace(' ', '_')}"
    response = requests.get(summary_url)
    if response.ok:
        data = response.json()
        return jsonify({
            "title": data.get("title"),
            "extract": data.get("extract"),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
        })
    return jsonify({"error": "Wikipedia summary request failed"}), response.status_code

@app.route("/fallback_gemini", methods=["POST"])
def fallback_gemini():
    user_message = request.json.get("message", "")

    if not user_message:
        return jsonify({"response": "Pesan kosong!"}), 400

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_message)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Gemini error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
