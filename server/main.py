from dotenv import load_dotenv
import os
import pathlib


# Load environment variables
basedir = pathlib.Path(__file__).parent
dotenv_path = os.path.join(basedir, ".env")
load_dotenv(dotenv_path)
# print(
#     f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}"
# )  # Debugging line

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials
from router import router
from config import get_settings

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )  # Load from .env
    firebase_admin.initialize_app(cred)

# Print Firebase App Project ID
print("Current App Name:", firebase_admin.get_app().project_id)

# FastAPI setup
app = FastAPI()
app.include_router(router)

import pprint


@app.on_event("startup")
async def debug_routes():
    pprint.pprint(app.routes)


origins = [get_settings().frontend_url]

# CORS settings (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust allowed origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
