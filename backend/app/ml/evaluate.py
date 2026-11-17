"""Evaluate a deterministic stratified holdout of the starter intent data."""
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
def main():
 data=[json.loads(x) for x in Path(__file__).with_name("intents.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
 X=[r["text"] for r in data]; y=[r["intent"] for r in data]
 Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
 model=Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2),strip_accents="unicode",sublinear_tf=True)),("clf",LogisticRegression(max_iter=2000,class_weight="balanced"))])
 model.fit(Xtr,ytr); pred=model.predict(Xte)
 print(f"Samples: {len(data)} | train: {len(Xtr)} | test: {len(Xte)}")
 print(f"Holdout accuracy: {accuracy_score(yte,pred):.3f}")
 print(classification_report(yte,pred,zero_division=0))
 print("Synthetic starter data only; validate with real, consented and anonymized queries before production claims.")
if __name__=="__main__": main()
