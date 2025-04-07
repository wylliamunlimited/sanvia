import os
from dotenv import load_dotenv

POPPLER_PATH = os.getenv("POPPLER_PATH")

if POPPLER_PATH:
    print(f"✅ POPPLER_PATH - {POPPLER_PATH} is Detected")
else:
    print("❌ POPPLER_PATH is NOT set.")
    raise ValueError("POPPLER_PATH is missing. Check your .env file.")
