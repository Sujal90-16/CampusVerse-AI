import joblib
from app.config import MODEL_PATH
_model = None

def predict_intent(message):
    global _model
    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    if _model is None:
        return "general", 0.0
    probs = _model.predict_proba([message])[0]
    idx = probs.argmax()
    label, confidence = str(_model.classes_[idx]), float(probs[idx])
    return (label, confidence) if confidence >= 0.24 else ("general", confidence)
