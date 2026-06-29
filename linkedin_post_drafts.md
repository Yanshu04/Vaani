# 🚀 Showcasing Vaani on LinkedIn

Here are three tailored drafts you can use to post about **Vaani** on LinkedIn. Choose the one that best fits your target audience (technical developers, AI enthusiasts, or product managers/general audience).

---

## Option 1: The Engineering Deep-Dive (Recommended)
*Best for: Software engineers, machine learning engineers, and developers who love clean architecture and local AI infrastructure.*

```text
🚀 I built "Vaani" — a multilingual, fully offline voice assistant running entirely on my local machine! No API keys, no internet, and zero data leakage.

Vaani listens to you in Hindi, Gujarati, or English, cleans up background noise, translates the input to English, queries a local LLM, and speaks the answer back.

Here is the engineering breakdown of how it works under the hood:

🎙️ Smart Audio Capture: Integrates WebRTC Voice Activity Detection (webrtcvad) to auto-detect silence and pause recording, along with dynamic noise reduction (noisereduce) to filter out ambient mic static.

🗣️ Speech-to-Text: Uses `faster-whisper` on CPU to transcribe speech and auto-detect the spoken language with high confidence.

🌐 Translation & Code-Switching: Utilizes Meta’s `NLLB-200` to translate regional inputs (Hindi/Gujarati/mixed) into English before passing them to the brain.

🧠 Local Brain: Powered by a local Ollama server running `qwen2.5:1.5b`. It processes prompts locally and streams responses dynamically.

🔊 Speech Synthesis: Generates voice responses using Windows' offline SAPI5 engine running in a separate background thread for high responsiveness.

🖥️ Streamlit Interface: A sleek dashboard providing real-time language detection badges, noise-level diagnostics, and audio playbacks.

Building this taught me a lot about local model serving, real-time audio pipeline optimization, and cross-language translation on consumer hardware.

Check out the architecture in the code snippet/video below! 👇

#LocalAI #GenerativeAI #SpeechToText #Python #OpenSource #Streamlit #Ollama #MachineLearning #NLP
```

---

## Option 2: High-Impact & Concise
*Best for: A general tech audience who wants to quickly see the value and UI/UX.*

```text
Privacy-first AI is the future. 🔒

I just completed building "Vaani", a personal voice assistant that runs 100% offline on my computer. You can speak to it in Hindi, Gujarati, or English, and it replies in real-time.

What makes it unique:
✅ Zero API Keys & Internet Required: Your voice data never leaves your computer.
✅ Multilingual Support: Built-in translation for Hindi and Gujarati.
✅ Audio Cleaning: Preprocesses live audio to remove background static before running transcription.
✅ Modern Streamlit UI: Shows live confidence score, detected language, and noise levels.

Tech Stack:
🛠️ faster-whisper (STT)
🛠️ Meta NLLB-200 (Translation)
🛠️ Ollama + Qwen (LLM)
🛠️ Streamlit & Python

Here's a quick demo of how it works: (Insert your demo video/screenshot!)

#OpenSource #ArtificialIntelligence #MachineLearning #Streamlit #Ollama #Python #PrivacyFirst
```

---

## Option 3: Story-Driven / Problem-Solver
*Best for: High engagement and storytelling style.*

```text
What if you could build a conversational voice assistant like Siri or Alexa, but completely offline, local, and private?

That was the challenge I set for myself, and the result is "Vaani" (🎙) — a voice assistant that speaks Hindi, Gujarati, and English, and runs on consumer-grade CPU hardware.

The biggest hurdle wasn't just connecting an LLM to a TTS engine. It was handling the unpredictability of real-world environments:
1. Microphone Static: Ambient room noise could break the speech recognizer. I added a real-time noise reduction step utilizing spectral gating.
2. Code-Switching: People rarely speak in one pure language; we often mix words. Meta's NLLB-200 translation handles mixed code-switching inputs beautifully.
3. Latency: Running models locally on CPU requires strict resource budgeting. Using faster-whisper and quantized models helped achieve near-real-time responses.

I'm excited to share this project and would love to hear your feedback on running models locally!

#AI #DeepLearning #VoiceAssistant #Python #Ollama #Privacy #DataScience
```

---

## 💡 Tips to Maximize Engagement

1. **Attach a Video Demo (Highly Recommended):** 
   Record a short 30–60 second screen recording of the Streamlit dashboard in action. 
   - Click the mic.
   - Speak a sentence in Hindi or Gujarati (e.g., *"आज का मौसम कैसा है?"* or *"તમારું નામ શું છે?"*).
   - Show how the app transcribes, translates, displays the Amber/Purple language badge, streams the response, and speaks the reply back.
2. **Add a Screenshot of the Directory/Code:**
   Show the clean project structure or a clean code snippet (like the `VoicePipeline` orchestrator).
3. **Include a Link to Your Github Repository:**
   If you have pushed this to GitHub, add the link at the bottom of your post!
