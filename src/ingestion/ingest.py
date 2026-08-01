import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from google import genai
import config

client = genai.Client(api_key=config.GEMINI_API_KEY)


def embed(text: str):
    response = client.models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=text
    )
    return response.embeddings[0].values


def run_ingestion():
    if not config.KNOWLEDGE_BASE_FILE.exists():
        raise FileNotFoundError(
            f"Knowledge base not found:\n{config.KNOWLEDGE_BASE_FILE}"
        )

    with open(config.KNOWLEDGE_BASE_FILE, "r", encoding="utf-8-sig") as f:
        knowledge = json.load(f)

    print(f"Loaded {len(knowledge)} knowledge records.", flush=True)

    vector_store = []

    for item in knowledge:
        print(f"Processing {item['id']}...", flush=True)

        document = (
            f"Category: {item['category']}\n"
            f"Question: {item['question']}\n"
            f"Answer: {item['answer']}"
        )

        try:
            embedding = embed(document)

            vector_store.append({
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "answer": item["answer"],
                "document": document,
                "embedding": embedding
            })

            print(f"   Stored {item['id']}", flush=True)

        except Exception as e:
            print(f"Error while processing {item['id']}: {e}", flush=True)
            break

    config.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    with open(config.VECTOR_STORE_FILE, "w", encoding="utf-8-sig") as f:
        json.dump(vector_store, f, ensure_ascii=False, indent=2)

    print("\nIngestion complete.", flush=True)
    print(f"Documents stored: {len(vector_store)}", flush=True)
    print(f"Vector store file: {config.VECTOR_STORE_FILE}", flush=True)


if __name__ == "__main__":
    run_ingestion()

