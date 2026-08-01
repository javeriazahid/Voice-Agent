import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from google.genai import types
from src.retrieval.retriever import search_knowledge_base

search_kb_declaration = types.FunctionDeclaration(
    name="search_knowledge_base",
    description=(
        "Search UMT's admissions knowledge base for information about "
        "programs, admission criteria, fees, how to apply, scholarships, "
        "campus facilities, or contact details. Use this whenever the user "
        "asks a question about UMT that requires factual information."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The user's question, rephrased as a clear search query."
            }
        },
        "required": ["query"],
    },
)

knowledge_base_tool = types.Tool(function_declarations=[search_kb_declaration])


def execute_tool_call(function_name: str, arguments: dict) -> str:
    if function_name == "search_knowledge_base":
        query = arguments.get("query", "")
        try:
            result = search_knowledge_base(query)
            if not result.strip():
                return "No relevant information found in the knowledge base."
            return result
        except Exception as e:
            return f"Error while searching knowledge base: {e}"

    return f"Unknown tool: {function_name}"
