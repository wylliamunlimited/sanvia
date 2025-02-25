# firebase_setup.py
import firebase_admin
from firebase_admin import credentials

import os

# Load Firebase credentials from environment variables
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not cred_path:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set in .env file")

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
