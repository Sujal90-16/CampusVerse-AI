import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "campusverse.db"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
JWT_SECRET = os.getenv("JWT_SECRET", "development-only-secret-please-rotate-before-production")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))
MODEL_PATH = Path(__file__).resolve().parent / "ml" / "intent_model.joblib"
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
