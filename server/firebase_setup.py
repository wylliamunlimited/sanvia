import os
import firebase_admin
from firebase_admin import credentials, auth

# Get the path to service account JSON
cred_path = "server/" + os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not cred_path:
    raise ValueError("❌ GOOGLE_APPLICATION_CREDENTIALS is NOT set properly.")

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

print("✅ Firebase Admin SDK initialized successfully!")
