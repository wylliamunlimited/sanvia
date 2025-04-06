import os
from dotenv import load_dotenv

POPPLER_PATH = os.getenv("POPPLER_PATH")

if POPPLER_PATH:
    print(f"✅ POPPLER_PATH - {POPPLER_PATH} is Detected")
else:
    print("❌ POPPLER_PATH is NOT set.")
    raise ValueError("POPPLER_PATH is missing. Check your .env file.")


CHROMA_DB_URL = os.getenv("CHROMA_DB_URL")

if CHROMA_DB_URL:
    print(f"✅ CHROMA_DB_URL - {CHROMA_DB_URL} is Detected")
else:
    print("❌ CHROMA_DB_URL is NOT set.")
    raise ValueError("CHROMA_DB_URL is missing. Check your .env file.")
