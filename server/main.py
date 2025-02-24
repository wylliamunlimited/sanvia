from server.router import router
from fastapi import FastAPI
import firebase_admin
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
firebase_admin.initialize_app()
# print("Current App Name:", firebase_admin.get_app().project_id)

origins = [get_settings().frontend_url]
