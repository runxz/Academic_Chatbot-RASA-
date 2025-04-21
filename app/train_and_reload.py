# /scripts/train_and_reload.py
import subprocess
from pathlib import Path
import shutil
from datetime import datetime
import time
import os
import psutil

# === CONFIG ===
MODEL_DIR = Path("models")
BACKUP_DIR = MODEL_DIR / "backups"
DATA_DIR = Path("data")
RASA_RUN_COMMAND = ["rasa", "run", "--enable-api", "--model", str(MODEL_DIR / "latest.tar.gz")]

# === ENSURE BACKUP DIR ===
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# === STEP 1: Generate Auto Training Data ===
print("🔄 Generating training data...")
subprocess.run(["python", "app/generate_nlu_auto.py"], check=True)
subprocess.run(["python", "app/generate_stories_auto.py"], check=True)
subprocess.run(["python", "app/generate_nlu_fallback.py"], check=True)

# === STEP 2: Train Model ===
print("📦 Training model...")
subprocess.run(["rasa", "train"], check=True)

# === STEP 3: Backup Previous Model ===
latest_model = max(MODEL_DIR.glob("*.tar.gz"), key=lambda f: f.stat().st_mtime)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_model_path = BACKUP_DIR / f"model_{timestamp}.tar.gz"
shutil.copy(latest_model, backup_model_path)
print(f"📦 Backed up model to: {backup_model_path}")

# === STEP 4: Auto-Restart Rasa Server (Cross-platform) ===
print("🔁 Restarting Rasa server with latest model...")

# Kill existing rasa run processes
for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
    try:
        if "rasa" in proc.info['name'] or (proc.info['cmdline'] and "rasa" in " ".join(proc.info['cmdline'])):
            proc.kill()
            time.sleep(1)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

# Start Rasa with latest model
log_file = open("rasa_server.log", "w")
subprocess.Popen(RASA_RUN_COMMAND, stdout=log_file, stderr=log_file)
print("🚀 Rasa server restarted with latest model.")
