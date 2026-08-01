import asyncio
import sys
import traceback
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import pyaudio
from google import genai
from google.genai import types

import config
from src.tools.knowledge_tool import knowledge_base_tool, execute_tool_call

client = genai.Client(api_key=config.GEMINI_API_KEY)

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

pya = pyaudio.PyAudio()

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


class VoiceAgent:
    def __init__(self):
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.audio_stream = None

    async def listen_audio(self):
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        print("Microphone listening... speak now (English, Urdu, or Punjabi).")
        while True:
            data = await asyncio.to_thread(
                self.audio_stream.read, CHUNK_SIZE, exception_on_overflow=False
            )
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def send_audio(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send_realtime_input(
                audio=types.Blob(data=msg["data"], mime_type=msg["mime_type"])
            )

    async def receive_audio(self):
        while True:
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue

                if text := response.text:
                    print("Gemini (text):", text)

                if response.tool_call:
                    for fc in response.tool_call.function_calls:
                        print(f"\n[Tool call] {fc.name}({fc.args})")
                        result = execute_tool_call(fc.name, fc.args)
                        print(f"[Tool result] {result[:200]}...\n")

                        await self.session.send_tool_response(
                            function_responses=[
                                types.FunctionResponse(
                                    id=fc.id,
                                    name=fc.name,
                                    response={"result": result},
                                )
                            ]
                        )

    async def play_audio(self):
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self):
        try:
            async with (
                client.aio.live.connect(model=config.LIVE_MODEL, config=LIVE_CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=10)

                print("Connected to Gemini Live. UMT Voice Agent ready.\n")

                tg.create_task(self.listen_audio())
                tg.create_task(self.send_audio())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

        except asyncio.CancelledError:
            pass
        except Exception:
            traceback.print_exc()
        finally:
            if self.audio_stream:
                self.audio_stream.close()


if __name__ == "__main__":
    print("Starting UMT Voice Agent (Ctrl+C to stop)...")
    asyncio.run(VoiceAgent().run())

