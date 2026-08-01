import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from google import genai
from google.genai import types

import config
from src.tools.knowledge_tool import knowledge_base_tool, execute_tool_call

app = FastAPI()

client = genai.Client(api_key=config.GEMINI_API_KEY)

LIVE_CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    system_instruction=config.SYSTEM_INSTRUCTION,
    tools=[knowledge_base_tool],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        )
    ),
)

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"


@app.get("/")
async def index():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Browser client connected.")

    try:
        async with client.aio.live.connect(
            model=config.LIVE_MODEL, config=LIVE_CONFIG
        ) as session:

            print("Connected to Gemini Live for this browser session.")

            async def browser_to_gemini():
                while True:
                    data = await websocket.receive_bytes()
                    await session.send_realtime_input(
                        audio=types.Blob(data=data, mime_type="audio/pcm;rate=16000")
                    )

            async def gemini_to_browser():
                while True:
                    turn = session.receive()
                    async for response in turn:
                        if data := response.data:
                            await websocket.send_bytes(data)
                            continue

                        if text := response.text:
                            await websocket.send_json({"type": "text", "text": text})

                        if response.tool_call:
                            for fc in response.tool_call.function_calls:
                                await websocket.send_json({
                                    "type": "tool_call",
                                    "name": fc.name,
                                    "args": fc.args
                                })

                                result = execute_tool_call(fc.name, fc.args)

                                await websocket.send_json({
                                    "type": "tool_result",
                                    "result": result[:300]
                                })

                                await session.send_tool_response(
                                    function_responses=[
                                        types.FunctionResponse(
                                            id=fc.id,
                                            name=fc.name,
                                            response={"result": result},
                                        )
                                    ]
                                )

            await asyncio.gather(browser_to_gemini(), gemini_to_browser())

    except WebSocketDisconnect:
        print("Browser client disconnected.")
    except Exception as e:
        print("Session error:", e)


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

