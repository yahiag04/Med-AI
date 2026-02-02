import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
WEIGHTS_PATH = BASE_DIR / "weights" / "best_pneumonia_net.pth"

APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "dev-insecure-change-me")
