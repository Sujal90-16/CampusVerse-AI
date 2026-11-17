import json
from pathlib import Path
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from app.config import MODEL_PATH

def main():
    data = [json.loads(x) for x in Path(__file__).with_name("intents.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    X, y = [r["text"] for r in data], [r["intent"] for r in data]
    model = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1,2), strip_accents="unicode")), ("clf", LogisticRegression(max_iter=1500, class_weight="balanced"))])
    model.fit(X, y)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Trained on {len(X)} examples / {len(set(y))} intents. Saved: {MODEL_PATH}")
    print("Starter dataset trained. Run python -m app.ml.evaluate for a deterministic holdout report; validate with real anonymized queries before production.")

if __name__ == "__main__":
    main()
