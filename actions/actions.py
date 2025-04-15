import requests
import pymysql
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from textblob import TextBlob
from fuzzywuzzy import fuzz

FLASK_API_URL = "http://127.0.0.1:5000"

# 🔹 Koneksi ke database menggunakan Flask API
def get_db_data(kategori_id):
    response = requests.get(f"{FLASK_API_URL}/informasi/{kategori_id}")
    if response.status_code == 200:
        return response.json()
    return None

# 🔹 Mencari jawaban terbaik berdasarkan kesamaan dengan judul & deskripsi
def find_best_match(user_question, kategori_id):
    data = get_db_data(kategori_id)
    if not data:
        return None

    best_match = None
    highest_score = 0

    for row in data:
        title_similarity = fuzz.partial_ratio(user_question.lower(), row["judul"].lower())
        description_similarity = fuzz.partial_ratio(user_question.lower(), row["deskripsi"].lower())

        max_similarity = max(title_similarity, description_similarity)  # Ambil skor tertinggi

        if max_similarity > highest_score:
            highest_score = max_similarity
            best_match = row["deskripsi"]  # Ambil deskripsi sebagai jawaban

    return best_match if highest_score > 60 else None  # Hanya jawab jika similarity > 60%

# 🔹 Analisis Sentimen
class ActionAnalyzeSentiment(Action):
    def name(self):
        return "action_analyze_sentiment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        user_message = tracker.latest_message.get("text")
        sentiment = TextBlob(user_message).sentiment.polarity

        if sentiment > 0:
            response = "Kamu tampak bahagia! Saya senang mendengarnya 😊"
        elif sentiment < 0:
            response = "Kamu terdengar sedih. Saya harap semuanya baik-baik saja."
        else:
            response = "Saya di sini jika kamu ingin berbicara lebih lanjut."

        dispatcher.utter_message(text=response)
        return []

# 🔹 Ambil Informasi dengan Analisis Pertanyaan
class ActionGetInformasi(Action):
    def name(self):
        return "action_get_informasi"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        user_message = tracker.latest_message.get("text")
        kategori_intent = tracker.latest_message['intent'].get('name')

        intent_map = {
            "informasi_pendaftaran": 1,
            "jadwal_pendaftaran": 2,
            "biaya_kuliah": 3,
            "persyaratan_pendaftaran": 4,
            "prosedur_seleksi": 5,
            "informasi_prodi": 6,
            "kurikulum_mata_kuliah": 7,
            "fasilitas_laboratorium": 8,
            "peluang_kerja": 9,
            "akreditasi_prestasi": 10,
            "kegiatan_mahasiswa": 11,
            "kontak_lokasi": 12,
            "beasiswa_dan_bantuan_keuangan": 13,
            "jadwal_kuliah": 14
        }

        if kategori_intent in intent_map:
            kategori_id = intent_map[kategori_intent]
            best_answer = find_best_match(user_message, kategori_id)

            if best_answer:
                dispatcher.utter_message(text=best_answer)
            else:
                dispatcher.utter_message(text=f"Maaf, saya tidak menemukan jawaban yang cocok untuk pertanyaan '{user_message}'. Bisa dijelaskan lebih detail?")
        else:
            dispatcher.utter_message(text="Saya tidak mengenali permintaan ini.")

        return []

# 🔹 Pencarian Informasi dari Wikipedia
class ActionSearchWikipedia(Action):
    def name(self):
        return "action_search_internet"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        query = tracker.latest_message.get("text")
        flask_api_url = "http://127.0.0.1:5000/search_wikipedia"

        try:
            response = requests.get(flask_api_url, params={"query": query})
            if response.status_code == 200:
                data = response.json()
                if "error" not in data:
                    dispatcher.utter_message(text=f"Ini yang saya temukan di Wikipedia Indonesia:\n{data['extract']}\nBaca lebih lanjut di: {data['url']}")
                else:
                    dispatcher.utter_message(text="Maaf, saya tidak menemukan informasi terkait di Wikipedia.")
            else:
                dispatcher.utter_message(text="Terjadi kesalahan saat mencari informasi di Wikipedia.")
        except Exception as e:
            dispatcher.utter_message(text="Terjadi kesalahan teknis saat mencari informasi.")
            print(f"Error: {e}")

        return []
