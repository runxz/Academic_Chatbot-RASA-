import pandas as pd
import requests
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm  # Untuk progress bar

# Path ke file CSV
csv_path = "C:/Users/Administrator/Documents/python/cb/chatbotv1/app/nlu_examples.csv"


# Load data
df = pd.read_csv(csv_path)
true_labels = []
pred_labels = []

# URL endpoint REST Rasa
RASA_API = "http://localhost:5005/model/parse"

# Proses dengan progress bar
for _, row in tqdm(df.iterrows(), total=len(df), desc="Menguji pertanyaan..."):
    payload = {"text": row["text"]}
    try:
        response = requests.post(RASA_API, json=payload)
        if response.status_code == 200:
            result = response.json()
            pred_intent = result.get("intent", {}).get("name", "unknown")
            true_labels.append(row["intent"])
            pred_labels.append(pred_intent)
        else:
            print(f"API Error: {response.status_code}")
            true_labels.append(row["intent"])
            pred_labels.append("api_error")
    except Exception as e:
        print(f"Error: {e}")
        true_labels.append(row["intent"])
        pred_labels.append("exception")

# 🔍 Evaluasi
print("\n📊 Classification Report:")
print(classification_report(true_labels, pred_labels))

# 🔁 Confusion Matrix
plt.figure(figsize=(12, 8))
cm = confusion_matrix(true_labels, pred_labels, labels=list(set(true_labels)))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=list(set(true_labels)), yticklabels=list(set(true_labels)))
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix of Rasa NLU Intent Predictions")
plt.tight_layout()
plt.show()
