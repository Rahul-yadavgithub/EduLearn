import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

# ---------------- DATABASE ----------------
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

# ---------------- JWT ----------------
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "default_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 168  # 7 days

# ---------------- ADMIN ----------------
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@learnhub.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ---------------- AI ----------------
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY")

# ---------------- CORS ----------------
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
