import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
LOGS_DIR = BASE_DIR / "logs"

KNOWLEDGE_BASE_FILE = DATA_DIR / "umt_admissions_knowledge_base.json"
VECTOR_STORE_FILE = STORAGE_DIR / "vector_store.json"

EMBEDDING_MODEL = "gemini-embedding-001"
LIVE_MODEL = "gemini-3.1-flash-live-preview"

SYSTEM_INSTRUCTION = (
    "You are a customer support agent for the University of Management "
    "and Technology (UMT), Lahore. Answer questions about admissions, "
    "programs, fees, and campus life using the information available to you. "
    "CRITICAL LANGUAGE RULE: You must detect the exact language the user "
    "speaks in - English, Urdu, or Punjabi - and respond in that exact same "
    "language. If the user speaks Punjabi, you must respond in Punjabi, not "
    "Urdu and not English, even if Punjabi is harder for you. Never default "
    "to Urdu or English when the user spoke Punjabi. Switch languages "
    "naturally if the user switches mid-conversation. Keep responses clear, "
    "concise, and conversational."
)

TOP_K_RESULTS = 3



