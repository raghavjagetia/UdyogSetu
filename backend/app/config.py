import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("UDYOGSETU_SECRET_KEY", "udyogsetu-dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12

DATABASE_URL = os.environ.get("UDYOGSETU_DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'udyogsetu.db')}")

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("UDYOGSETU_ALLOWED_ORIGINS", _default_origins).split(",")
    if origin.strip()
]
