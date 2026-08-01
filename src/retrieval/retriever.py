import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
from google import genai
import config

client = genai.Client(api_key=config.GEMINI_API_KEY)

_vector_store = None
_store_matrix = None


def _load_vector_store():
    global _vector_store, _store_matrix

    if _vector_store is not None:
        return

    if not config.VECTOR_STORE_FILE.exists():
        raise FileNotFoundError(
            f"Vector store not found. Run ingestion first.\n{config.VECTOR_STORE_FILE}"
        )

    # Fix: Use utf-8-sig to handle BOM
    with open(config.VECTOR_STORE_FILE, "r", encoding="utf-8-sig") as f:
        _vector_store = json.load(f)

    _store_matrix = np.array([item["embedding"] for item in _vector_store])


def embed_query(text: str):
    response = client.models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=[text]
    )
    return response.embeddings[0].values


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search_knowledge_base(query: str, top_k: int = None) -> str:
    _load_vector_store()

    top_k = top_k or config.TOP_K_RESULTS

    query_vector = embed_query(query)

    scores = []
    for i, item in enumerate(_vector_store):
        score = cosine_similarity(query_vector, _store_matrix[i])
        scores.append((score, item))

    scores.sort(key=lambda x: x[0], reverse=True)
    top_results = scores[:top_k]

    formatted = "\n\n".join(
        f"[{item['category']}] {item['document']}"
        for score, item in top_results
    )

    return formatted


if __name__ == "__main__":
    print("Retriever ready. Type a question (or exit to quit).\n")
    while True:
        q = input("Ask: ")
        if q.lower() == "exit":
            break
        try:
            result = search_knowledge_base(q)
            print("\n" + result + "\n")
        except Exception as e:
            print("ERROR:", e)
