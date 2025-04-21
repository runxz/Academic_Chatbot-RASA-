# /scripts/generate_nlu_fallback.py
import json
import pymysql
from pathlib import Path

OUTPUT_FILE = Path("data/nlu_fallback.yml")

# === DB CONNECTION ===
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="rasa",
    charset="utf8mb4"
)

CONFIDENCE_THRESHOLD = 0.5
FALLBACK_INTENT_NAME = "nlu_fallback"

# === EXTRACT LOW CONFIDENCE TEXTS THAT TRIGGERED FALLBACK ===
def extract_fallback_examples():
    cursor = conn.cursor()
    cursor.execute("SELECT sender_id, type_name, timestamp, data FROM events ORDER BY sender_id, timestamp")
    rows = cursor.fetchall()

    fallback_texts = []
    last_user_text = None
    last_confidence = 1.0

    for sender_id, type_name, timestamp, data_json in rows:
        try:
            data = json.loads(data_json)
            if type_name == "user":
                last_user_text = data.get("text", None)
                last_confidence = data.get("parse_data", {}).get("intent", {}).get("confidence", 1.0)
            elif type_name == "action" and data.get("name") == "action_default_fallback":
                if last_user_text and last_confidence < CONFIDENCE_THRESHOLD:
                    fallback_texts.append((last_user_text.strip(), last_confidence))
        except Exception as e:
            print(f"Skipping event due to error: {e}")

    # Deduplicate by text
    unique_texts = {}
    for text, confidence in fallback_texts:
        if text not in unique_texts or confidence < unique_texts[text]:
            unique_texts[text] = confidence

    return unique_texts

# === WRITE TO YAML ===
def write_nlu_fallback_yml(texts_with_conf):
    lines = ["version: '3.1'", "nlu:", f"- intent: {FALLBACK_INTENT_NAME}", "  examples: |"]
    for text, conf in texts_with_conf.items():
        lines.append(f"    - {text}  # confidence: {conf:.2f}")

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ NLU fallback data written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    examples = extract_fallback_examples()
    write_nlu_fallback_yml(examples)
