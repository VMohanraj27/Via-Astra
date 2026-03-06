import os
from dotenv import load_dotenv

load_dotenv(".env")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MODEL_NAME = "gemini-2.5-flash"

MLFLOW_TRACKING_URI = "http://localhost:5000"