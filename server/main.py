from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
import os
import pathlib

from server.router import router
from server.config import get_settings

# Load environment variables
basedir = pathlib.Path(__file__).parents[1]  # Project root
load_dotenv(os.path.join(basedir, "server", ".env"))

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))  # Load from .env
    firebase_admin.initialize_app(cred)

# Print Firebase App Project ID
print("Current App Name:", firebase_admin.get_app().project_id)

# FastAPI setup
app = FastAPI()
app.include_router(router)

origins = [get_settings().frontend_url]

# CORS settings (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust allowed origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
