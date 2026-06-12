# Vaani 🎙

Vaani is a voice assistant that runs completely offline on your computer. You can speak to it in **Hindi, Gujarati, or English**. It filters out background noise, transcribes and translates your voice to English, gets a response from a local AI model (via Ollama), and speaks the answer back to you.

No API keys, no internet required, and your audio data never leaves your machine.

---

## What's inside?
- **STT (Speech-to-Text):** `faster-whisper` for multilingual transcription.
- **Translation:** Meta's `NLLB-200` to translate Hindi/Gujarati inputs to English.
- **Brain:** Local `Ollama` server (default is `qwen2.5:1.5b`).
- **TTS (Text-to-Speech):** Offline SAPI5 (Windows voices like David or Zira) running in a background thread.
- **Audio Cleaning:** WebRTC Voice Activity Detection (`webrtcvad`) and `noisereduce` to clean mic static.

---

## Getting Started

### 1. Requirements
- Python 3.10 or higher.
- A working microphone.
- [Ollama](https://ollama.com/) installed and running.
- Around 5 GB of free disk space (to store the offline models).

### 2. Setup
Open your terminal in the project folder and run:

```bash
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install requirements
pip install -r requirements.txt

# 3. Download the speech & translation models
python download_models.py

# 4. Pull the LLM model in Ollama
ollama pull qwen2.5:1.5b
```

---

## Running the App
Make sure your Ollama app is running in the background, then launch the UI:

```bash
streamlit run frontend/dashboard.py
```

It will automatically open a tab in your browser (usually at `http://localhost:8501`).

---

## How to use it
1. **By Voice:** Click the **🎙** button, speak in Hindi, Gujarati, or English, and wait. The app stops recording when you pause speaking, generates a response, and plays the voice response automatically.
2. **By Text:** Type your query in the input box at the bottom. Hindi or Gujarati inputs are translated to English before going to the LLM.
3. **Sidebar Settings:** You can change the Whisper model size (use `tiny` if your computer is slow, or `medium` for better accuracy), turn voice output on/off, change the assistant voice, or clear the chat history.

---

## Project Structure
Here is where the main files are located:
```text
Vaani/
├── app/
│   ├── core/
│   │   ├── audio_capture.py       # Recording and silence detection
│   │   ├── audio_denoiser.py      # Noise cleaning
│   │   ├── stt_engine.py          # Whisper speech-to-text
│   │   ├── translation_engine.py  # NLLB translation
│   │   ├── response_generator.py  # Local Ollama integration
│   │   └── voice_synthesizer.py   # Text-To-Speech (TTS)
│   └── services/
│       └── pipeline.py            # Orchestrator linking engines together
├── frontend/
│   └── dashboard.py               # Streamlit web UI
├── download_models.py             # One-time downloader script
└── requirements.txt               # Dependencies
```
