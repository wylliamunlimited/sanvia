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
from routers import firebase_auth
from routers import firebase_db
from dependencies.firebase_dependencies import get_settings, initialize_firebase, get_firestore_client

## initializing firebase sdk
initialize_firebase()

# Print Firebase App Project ID
print("Current App Name:", firebase_admin.get_app().project_id)


# FastAPI setup
app = FastAPI()
app.include_router(firebase_auth.router)
app.include_router(firebase_db.router)

import pprint


@app.on_event("startup")
async def debug_routes():
    pprint.pprint(app.routes)
    
@app.get("/")
def hello():
    """Server is running route to test if the app is running."""
    return {"msg": "Server is running"}


origins = [get_settings().frontend_url]

# CORS settings (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust allowed origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



