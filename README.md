# Vaani 🎙

Vaani (meaning "voice" in Hindi/Gujarati) is a local, offline, voice-activated multilingual chatbot that transcribes and translates spoken Hindi, English, or Gujarati, sends the English prompt to a local LLM, and displays the conversational reply. Designed to operate 100% locally and offline, the project requires zero external API keys and guarantees that your voice data never leaves your machine.

## Prerequisites

- **Python**: version 3.10 or higher
- **Ollama**: Installed and running locally on your machine. Download from [ollama.com](https://ollama.com/).
- **Disk Space**: At least 5 GB of free space to accommodate offline models (~2.1 GB for STT/translation, ~950 MB for the Qwen LLM).
- **Audio hardware**: An active working microphone.

## Installation & Setup

1. **Clone the repository** (or navigate to the workspace directory):
   ```bash
   cd Vaani
   ```

2. **Set up a Python Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the One-Time Speech & Translation Model Downloader**:
   This script pre-caches the Whisper and Helsinki-NLP models locally under the `./models` directory so transcription and translation work completely offline.
   ```bash
   python download_models.py
   ```

5. **Set up local Ollama & Pull the LLM Chat Model**:
   - Ensure you have downloaded and installed [Ollama](https://ollama.com/).
   - Open your terminal and pull the default recommended lightweight chat model (`qwen2.5:1.5b`):
     ```bash
     ollama pull qwen2.5:1.5b
     ```
   - Make sure the Ollama application is running in the background.

## Running the Application

1. Make sure your local **Ollama** service is running in the background.
2. Launch the Streamlit frontend dashboard:
   ```bash
   streamlit run frontend/dashboard.py
   ```
3. A web page will automatically load in your default browser (typically at `http://localhost:8502`).

### How to Interact
Once the app loads, you have two ways to chat with Vaani:
- **Voice Chat**: Click the red **🎙 Start Speaking** button, speak your query in Hindi, Gujarati, or English, and wait. The app automatically stops recording when it detects silence (or after a timeout) and generates a reply.
- **Text Chat**: Scroll to the bottom and use the **native chat input box**. Type your message in Hindi, Gujarati, or English and press Enter. Non-English text is automatically translated to English before querying the model.

## Reference Tables

### Supported Languages
| Language | Code | Native Script Examples |
| :--- | :---: | :--- |
| **English** | `en` | "How are you doing today?" |
| **Hindi** | `hi` | "नमस्ते, आप कैसे हैं?" |
| **Gujarati** | `gu` | "નમસ્તે, તમે કેમ છો?" |

### Whisper Model Options
Select the Whisper model size in the application sidebar depending on your CPU capabilities:
| Model Size | Speed on CPU | Accuracy | Memory Footprint |
| :--- | :--- | :--- | :--- |
| **tiny** | Extremely Fast | Low (prone to misspellings) | ~70 MB |
| **small** | Fast | Balanced | ~460 MB |
| **medium** *(Default)* | Moderate | High | ~1.5 GB |
| **large-v2** | Slow | Maximum / Human-Level | ~3.0 GB |

## Troubleshooting

- **Microphone Access / Permission Denied Error**:
  - Make sure your operating system settings allow apps to access your microphone.
  - On Windows, go to *Settings > Privacy & security > Microphone* and ensure "Let desktop apps access your microphone" is toggled ON.
- **"No speech detected" / "Low confidence" Error**:
  - Speak closer to the microphone.
  - Make sure the room has minimal ambient noise. The noise indicator in the app should register as green ("low") or orange ("medium").
- **Model Loading Failures**:
  - Ensure that the download script completes successfully with checkmarks.
  - Verify that the `./models` directory contains the model subfolders.
