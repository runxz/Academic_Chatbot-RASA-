# /scripts/generate_nlu_auto.py
import json
import pymysql
from pathlib import Path
from collections import defaultdict

# === DB CONNECTION ===
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="rasa",
    charset="utf8mb4"
)

# === PARAMS ===
CONFIDENCE_THRESHOLD = 0.5
OUTPUT_FILE = Path("data/nlu_auto.yml")

# === FETCH LOW CONFIDENCE MESSAGES ===
def fetch_low_confidence_messages():
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM events WHERE type_name = 'user'")

    examples_by_intent = defaultdict(list)

    for (data_json,) in cursor.fetchall():
        try:
            event = json.loads(data_json)
            parse_data = event.get("parse_data", {})
            intent = parse_data.get("intent", {}).get("name", "fallback_intent")
            confidence = parse_data.get("intent", {}).get("confidence", 1.0)
            text = event.get("text", "")

            if confidence < CONFIDENCE_THRESHOLD and text:
                examples_by_intent[intent].append(text.strip())
        except Exception as e:
            print(f"Error parsing event: {e}")

    return examples_by_intent

# === WRITE TO YAML ===
def write_nlu_yml(examples_by_intent):
    lines = ["version: '3.1'", "nlu:"]
    for intent, examples in examples_by_intent.items():
        lines.append(f"- intent: {intent}")
        lines.append("  examples: |")
        for ex in set(examples):
            lines.append(f"    - {ex}")

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ NLU data written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    examples = fetch_low_confidence_messages()
    write_nlu_yml(examples)
