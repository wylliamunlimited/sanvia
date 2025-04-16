# = = = = = = = = = = = = = = = = = = = Load Env Variable = = = = = = = = = = = = = = = = = = = =
from dotenv import load_dotenv
import os
import pathlib

basedir = pathlib.Path(__file__).parent
dotenv_path = os.path.join(basedir, ".env")
load_dotenv(dotenv_path)
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


# = = = = = = = = = = = = = = = = = = = = = = Imports = = = = = = = = = = = = = = = = = = = = = =
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials
from routers import (
    firebase_auth,
    firebase_db,
    search,
    ai_agent,
    document_processing,
    health_connect_sdk,
    health_data,
)
from dependencies.firebase_dependencies import (
    get_settings,
    initialize_firebase,
    get_firestore_client,
)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

# = = = = = = = = = = = = = = = = = = = Initialization  = = = = = = = = = = = = = = = = = = = = =
## initializing firebase sdk
initialize_firebase()
# Print Firebase App Project ID
print("Current App Name:", firebase_admin.get_app().project_id)
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


# = = = = = = = = = = = = = = = = = = = = Server Router = = = = = = = = = = = = = = = = = = = = =
# FastAPI setup
# Set up the routes for the application
app = FastAPI()
app.include_router(firebase_auth.router)
app.include_router(firebase_db.router)
app.include_router(search.router)
app.include_router(ai_agent.router)
app.include_router(document_processing.router)
app.include_router(health_connect_sdk.router)
app.include_router(health_data.router)
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


import pprint


@app.on_event("startup")
async def debug_routes():
    pprint.pprint(app.routes)


@app.get("/")
def hello():
    """Server is running route to test if the app is running."""
    return {"msg": "Server is running"}


@app.get("/health")
def health_check():
    """Health Check Endpoint to ensure server is running"""
    return {"status": "healthy"}


origins = ["*"]  # For development, allow all origins

# CORS settings (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust allowed origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
