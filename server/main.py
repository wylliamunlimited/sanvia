from server.router import router
from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
import pathlib
from fastapi.middleware.cors import CORSMiddleware
import os
from server.config import get_settings


# we need to load the env file because it contains the GOOGLE_APPLICATION_CREDENTIALS
basedir = pathlib.Path(__file__).parents[1]
load_dotenv(basedir / ".env")
app = FastAPI()
app.include_router(router)
cred = credentials.ApplicationDefault()  # Uses GOOGLE_APPLICATION_CREDENTIALS from .env
firebase_admin.initialize_app(cred)
# print("Current App Name:", firebase_admin.get_app().project_id)


origins = [get_settings().frontend_url]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
