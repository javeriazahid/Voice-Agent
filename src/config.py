import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
LOGS_DIR = BASE_DIR / "logs"

# File paths
KNOWLEDGE_BASE_FILE = DATA_DIR / "umt_admissions_knowledge_base.json"
VECTOR_STORE_FILE = STORAGE_DIR / "vector_store.json"

# Model Configuration
EMBEDDING_MODEL = "models/gemini-embedding-001"
TOP_K_RESULTS = 3

# Validate critical paths
if not KNOWLEDGE_BASE_FILE.exists():
    raise FileNotFoundError(f"Knowledge base not found: {KNOWLEDGE_BASE_FILE}")

if not VECTOR_STORE_FILE.exists():
    raise FileNotFoundError(f"Vector store not found: {VECTOR_STORE_FILE}. Run ingestion first.")
