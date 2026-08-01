const micBtn = document.getElementById("micBtn");
const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
const conversationEl = document.getElementById("conversation");
const devToggle = document.getElementById("devToggle");

devToggle.addEventListener("change", () => {
  logEl.style.display = devToggle.checked ? "block" : "none";
});

function addBubble(text, who) {
  const div = document.createElement("div");
  div.className = "bubble " + who;
  div.textContent = text;
  conversationEl.appendChild(div);
  conversationEl.scrollTop = conversationEl.scrollHeight;
}

let ws = null;
let audioContext = null;
let processor = null;
let micStream = null;
let recording = false;

let playbackContext = null;
let playbackTime = 0;

function log(text, cls = "") {
  const div = document.createElement("div");
  div.className = "log-line " + cls;
  div.textContent = text;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

function floatTo16BitPCM(float32Array) {
  const buffer = new ArrayBuffer(float32Array.length * 2);
  const view = new DataView(buffer);
  let offset = 0;
  for (let i = 0; i < float32Array.length; i++, offset += 2) {
    let s = Math.max(-1, Math.min(1, float32Array[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return buffer;
}

function downsampleTo16k(buffer, inputSampleRate) {
  if (inputSampleRate === 16000) return buffer;
  const ratio = inputSampleRate / 16000;
  const newLength = Math.round(buffer.length / ratio);
  const result = new Float32Array(newLength);
  for (let i = 0; i < newLength; i++) {
    result[i] = buffer[Math.round(i * ratio)];
  }
  return result;
}

async function startRecording() {
  ws = new WebSocket(`ws://${location.host}/ws`);
  ws.binaryType = "arraybuffer";

  ws.onopen = async () => {
    statusEl.textContent = "Connected. Listening...";

    micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(micStream);

    processor = audioContext.createScriptProcessor(4096, 1, 1);
    source.connect(processor);
    processor.connect(audioContext.destination);

    processor.onaudioprocess = (e) => {
      if (!recording) return;
      const input = e.inputBuffer.getChannelData(0);
      const downsampled = downsampleTo16k(input, audioContext.sampleRate);
      const pcm16 = floatTo16BitPCM(downsampled);
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(pcm16);
      }
    };

    playbackContext = new AudioContext({ sampleRate: 24000 });
    playbackTime = playbackContext.currentTime;
  };

  ws.onmessage = (event) => {
    if (typeof event.data === "string") {
      const msg = JSON.parse(event.data);
      if (msg.type === "tool_call") {
        log(`🔧 Calling: ${msg.name}(${JSON.stringify(msg.args)})`, "log-tool");
      } else if (msg.type === "tool_result") {
        log(`✅ ${msg.result}`, "log-result");
      } else if (msg.type === "text") {
        log(`💬 ${msg.text}`);
        addBubble(msg.text, "agent");
      }
      return;
    }

    playPCM16(event.data);
  };

  ws.onclose = () => {
    statusEl.textContent = "Disconnected.";
  };

  ws.onerror = (err) => {
    console.error(err);
    statusEl.textContent = "Connection error.";
  };
}

function playPCM16(arrayBuffer) {
  const int16 = new Int16Array(arrayBuffer);
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) {
    float32[i] = int16[i] / 32768;
  }

  const audioBuffer = playbackContext.createBuffer(1, float32.length, 24000);
  audioBuffer.getChannelData(0).set(float32);

  const source = playbackContext.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(playbackContext.destination);

  const now = playbackContext.currentTime;
  const startAt = Math.max(now, playbackTime);
  source.start(startAt);
  playbackTime = startAt + audioBuffer.duration;
}

function stopRecording() {
  recording = false;
  if (processor) processor.disconnect();
  if (micStream) micStream.getTracks().forEach((t) => t.stop());
  if (ws) ws.close();
  statusEl.textContent = "Stopped.";
}

micBtn.addEventListener("click", async () => {
  if (!recording) {
    recording = true;
    micBtn.classList.add("recording");
    micBtn.textContent = "⏹️";
    await startRecording();
  } else {
    recording = false;
    micBtn.classList.remove("recording");
    micBtn.textContent = "🎤";
    stopRecording();
  }
});
