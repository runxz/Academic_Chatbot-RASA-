# /scripts/generate_stories_auto.py
import json
import pymysql
from pathlib import Path
from collections import defaultdict

OUTPUT_FILE = Path("data/stories_auto.yml")

# === DB CONNECTION ===
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="rasa",
    charset="utf8mb4"
)

# === EXTRACT DIALOGUES FROM EVENTS ===
def extract_stories():
    cursor = conn.cursor()
    cursor.execute("SELECT sender_id, type_name, timestamp, data FROM events ORDER BY sender_id, timestamp")
    rows = cursor.fetchall()

    dialogues = defaultdict(list)

    for sender_id, type_name, timestamp, data_json in rows:
        try:
            data = json.loads(data_json)
            if type_name == "user":
                intent = data.get("parse_data", {}).get("intent", {}).get("name")
                if intent:
                    dialogues[sender_id].append(f"- intent: {intent}")
            elif type_name == "action":
                action = data.get("name")
                if action:
                    dialogues[sender_id].append(f"- action: {action}")
        except Exception as e:
            print(f"Skipping event due to error: {e}")

    return dialogues

# === WRITE TO YAML ===
def write_stories_yml(dialogues):
    lines = ["version: '3.1'", "stories:"]
    for i, (sender_id, steps) in enumerate(dialogues.items(), start=1):
        if len(steps) < 2:
            continue  # Skip too-short stories
        if not any("action_default_fallback" in step for step in steps):
            continue  # Skip stories without fallback

        lines.append(f"- story: fallback_story_{i}")
        lines.append("  steps:")
        for step in steps:
            lines.append(f"    {step}")

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Fallback stories written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    dialogue_data = extract_stories()
    write_stories_yml(dialogue_data)
