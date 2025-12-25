import os
from dotenv import load_dotenv
from pathlib import Path

# -------------------------------------------------
# LOAD ENV
# -------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

# -------------------------------------------------
# DATABASE
# -------------------------------------------------
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

# -------------------------------------------------
# JWT
# -------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "default_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 168  # 7 days

# -------------------------------------------------
# ADMIN
# -------------------------------------------------
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@learnhub.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# -------------------------------------------------
# AI KEYS
# -------------------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# -------------------------------------------------
# CORS (SAFE PARSING)
# -------------------------------------------------
# -------------------------------------------------
# CORS (ROBUST & RENDER-SAFE)
# -------------------------------------------------

# -------------------------------------------------
# CORS (RENDER-SAFE, NON-EMPTY)
# -------------------------------------------------

_raw_origins = os.getenv("CORS_ORIGINS")

if _raw_origins and _raw_origins.strip():
    CORS_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]
else:
    # ✅ HARD SAFE DEFAULT (Render does NOT load .env reliably)
    CORS_ORIGINS = [
        "https://edulearn-frontend-nsg7.onrender.com",
        "http://localhost:3000",
        "http://localhost:5173",
    ]

