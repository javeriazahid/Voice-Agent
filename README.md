# UMT Voice Agent

A multilingual, real-time voice assistant for UMT (University of Management and Technology) admissions — built with Google's Gemini Live API and Retrieval-Augmented Generation (RAG).

Speak a question in **English, Urdu, or Punjabi**, and the agent understands, retrieves the relevant UMT admissions information, and responds naturally in the same language — all in real time.

## Features

- 🎙️ **Real-time voice conversation** using Gemini's Live API (native speech-to-speech, no separate STT/TTS pipeline)
- 🌐 **Multilingual support** — automatically detects and responds in English, Urdu, or Punjabi
- 📚 **RAG-based answers** — retrieves accurate information from a UMT admissions knowledge base instead of relying on the model's general knowledge
- 🔧 **Tool calling** — Gemini decides when to query the knowledge base mid-conversation
- 🖥️ **Web interface** — simple browser-based mic button UI, no app installation needed
- 🛠️ **Developer mode** — optional toggle to view technical logs (tool calls, retrieved data) for debugging

## Tech Stack

| Component | Technology |
|---|---|
| Voice / Conversation | Gemini Live API (`gemini-3.1-flash-live-preview`) |
| Embeddings | Gemini Embedding API (`gemini-embedding-001`) |
| Retrieval | Custom vector store (NumPy cosine similarity) |
| Backend | FastAPI + WebSockets |
| Frontend | Vanilla JavaScript, Web Audio API |

## Project Structure

```
voice agent/
├── server.py                  # FastAPI backend — WebSocket bridge to Gemini Live
├── config.py                  # Centralized configuration
├── data/
│   └── umt_admissions_knowledge_base.json   # Source knowledge base (Q&A pairs)
├── storage/
│   └── vector_store.json      # Generated embeddings (from ingestion)
├── frontend/
│   ├── index.html             # Web UI
│   └── app.js                 # Mic capture, WebSocket streaming, audio playback
└── src/
    ├── ingestion/
    │   └── ingest.py           # Builds the vector store from the knowledge base
    ├── retrieval/
    │   └── retriever.py        # Cosine similarity search over embeddings
    ├── tools/
    │   └── knowledge_tool.py   # Gemini function-calling tool definition
    └── voice/
        └── live_session.py     # Terminal-based voice loop (for quick testing)
```

## Setup

### 1. Clone and install dependencies
```bash
git clone https://github.com/YOUR_USERNAME/umt-voice-agent.git
cd umt-voice-agent
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Add your Gemini API key
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_key_here
```
Get a key from [Google AI Studio](https://aistudio.google.com).

### 3. Build the knowledge base (if not already present)
```bash
python src/ingestion/ingest.py
```

### 4. Run the web app
```bash
python server.py
```
Open **http://localhost:8000** in your browser, click the mic button, and start talking.

## How It Works

1. The browser captures microphone audio and streams it to the FastAPI backend over WebSocket.
2. The backend forwards the audio to Gemini's Live API in real time.
3. When the user asks something requiring factual UMT information, Gemini calls the `search_knowledge_base` tool.
4. The tool embeds the query, searches the vector store for the most relevant entries, and returns them to Gemini.
5. Gemini generates a spoken response grounded in that retrieved information, in the same language the user spoke.
6. The response audio streams back to the browser and plays automatically.

## Notes

- Currently scoped to **UMT admissions** information (programs, fees, criteria, how to apply, contact details). Can be expanded to cover LMS or student portal use cases in future phases.
- Punjabi language support is functional but may be less mature than English/Urdu due to lower training data availability for the underlying model.
- Free-tier API quotas apply — check [Google AI Studio](https://aistudio.google.com) for current limits.

## License

This project is for educational/demonstration purposes.
