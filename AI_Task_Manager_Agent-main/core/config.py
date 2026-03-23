# core/config.py

import os

# --- Ollama Configuration ---
# Use 127.0.0.1 instead of localhost for better cross-platform compatibility
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3:8b")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")

# --- FAISS/Vector Store Configuration ---
FAISS_INDEX_PATH = "data/faiss_index"

# --- Agent Configuration ---
CATEGORIES = ["Development", "Research", "Admin", "Urgent"]
PRIORITIES = ["High", "Medium", "Low"]


# Ensure the data directory exists
os.makedirs(FAISS_INDEX_PATH, exist_ok=True)

print(f"Configuration loaded. LLM: {LLM_MODEL}, Embeddings: {EMBEDDING_MODEL}")
