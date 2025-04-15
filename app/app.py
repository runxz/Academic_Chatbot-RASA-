from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import mysql.connector

app = Flask(__name__)

CORS(app)

# Rasa server API URL
RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"

# Konfigurasi Database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Ganti dengan password database Anda
    database="chatbot_db"
)
cursor = db.cursor()

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_message = request.json["message"]
    
    # Send message to Rasa
    response = requests.post(RASA_API_URL, json={"sender": "user", "message": user_message})
    
    if response.status_code == 200:
        rasa_reply = response.json()
        bot_response = rasa_reply[0]["text"] if rasa_reply else "Maaf, saya tidak mengerti."
    else:
        bot_response = "Maaf, ada kesalahan dalam komunikasi dengan bot."

    return jsonify({"response": bot_response})

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
