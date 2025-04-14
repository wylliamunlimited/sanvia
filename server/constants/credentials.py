import os
from dotenv import load_dotenv
import json

load_dotenv()

# Load environment variables

# Check if FIREBASE_ADMIN_SDK_KEY is loaded
# 🚨🚨🚨 IMPORTANT 🚨🚨🚨: the env variable has to be the json content inside the key file, ❌❌❌ NOT the path to the file
#                                        so you need to copy the content of the file and paste it in the env variable
#                                        This is because deployment on Railway doesn't allow file upload
FIREBASE_ADMIN_API_KEY = os.getenv("FIREBASE_ADMIN_SDK_KEY")
if FIREBASE_ADMIN_API_KEY:
    print(f"✅ FIREBASE_ADMIN_SDK_KEY is Detected")

    import json
    FIREBASE_ADMIN_API_KEY = json.loads(
        FIREBASE_ADMIN_API_KEY
    )  ## 🚨🚨🚨 DON'T CHANGE. If needed, change the env variable to json
else:
    print("❌ FIREBASE_ADMIN_SDK_KEY is NOT set.", FIREBASE_ADMIN_API_KEY)
    raise ValueError(
        "Firebase service account credentials is missing. Check your .env file."
    )


FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")
if FIREBASE_WEB_API_KEY:
    print(f"✅ FIREBASE_WEB_API_KEY is Detected")
else:
    print("❌ FIREBASE_WEB_API_KEY is NOT set.")
    raise ValueError(
        "Firebase project web api key file path is missing. Check your .env file."
    )


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    print(f"✅ OPENAI_API_KEY is Detected")
else:
    print("❌ OPENAI_API_KEY is NOT set.")
    raise ValueError("OpenAI API key is missing. Check your .env file.")


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if TAVILY_API_KEY:
    print(f"✅ TAVILY_API_KEY is Detected")
else:
    print("❌ TAVILY_API_KEY is NOT set.")
    raise ValueError("Tavily API key is missing. Check your .env file.")


CHROMA_DB_ACCESS_CLIENT_ID = os.getenv("CHROMA_DB_ACCESS_CLIENT_ID")

if CHROMA_DB_ACCESS_CLIENT_ID:
    print(f"✅ CHROMA_DB_ACCESS_CLIENT_ID is Detected")
else:
    print("❌ CHROMA_DB_ACCESS_CLIENT_ID is NOT set.")
    raise ValueError("CHROMA DB API Client ID is missing. Check your .env file.")

    
CHROMA_DB_ACCESS_SECRET = os.getenv("CHROMA_DB_ACCESS_SECRET")

if CHROMA_DB_ACCESS_SECRET:
    print(f"✅ CHROMA_DB_ACCESS_SECRET is Detected")
else:
    print("❌ CHROMA_DB_ACCESS_SECRET is NOT set.")
    raise ValueError("CHROMA DB API Client Secret is missing. Check your .env file.")


JWT_HASH_KEY = os.getenv("JWT_HASH_KEY")

if JWT_HASH_KEY:
    print(f"✅ JWT_HASH_KEY is Detected")
else:
    print("❌ JWT_HASH_KEY is NOT set.")
    raise ValueError("JWT hash key is missing. Check your .env file.")


WHOOP_CLIENT_ID = os.getenv("WHOOP_CLIENT_ID")

if WHOOP_CLIENT_ID:
    print(f"✅ WHOOP_CLIENT_ID is Detected")
else:
    print("❌ WHOOP_CLIENT_ID is NOT set.")
    raise ValueError("WHOOP Client ID is missing. Check your .env file.")


WHOOP_CLIENT_SECRET = os.getenv("WHOOP_CLIENT_SECRET")

if WHOOP_CLIENT_SECRET:
    print(f"✅ WHOOP_CLIENT_SECRET is Detected")
else:
    print("❌ WHOOP_CLIENT_SECRET is NOT set.")
    raise ValueError("WHOOP Client Secret is missing. Check your .env file.")
