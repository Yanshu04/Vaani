import streamlit as st
import datetime
import traceback
import sys
import time
from pathlib import Path

# Add project root to path to ensure imports work correctly when running streamlit
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.services.pipeline import VoicePipeline
from app.core.audio_capture import record_until_silence, push_to_talk_record, ThreadedRecorder
from app.core.audio_denoiser import reduce_noise, estimate_noise_level
from app.core.voice_synthesizer import TTSGenerator

# Configure Streamlit page layout
st.set_page_config(page_title="Vaani", page_icon="🎙", layout="centered")

# Custom CSS for styling the UI and badges
st.markdown("""
<style>
    .badge {
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-right: 6px;
        vertical-align: middle;
    }
    .badge-hi { background-color: #FFA000; } /* Amber */
    .badge-en { background-color: #1976D2; } /* Blue */
    .badge-gu { background-color: #7B1FA2; } /* Purple */
    .noise-dot {
        font-size: 16px;
        vertical-align: middle;
        margin-right: 4px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Caching the pipeline resource to avoid reloading models on every interaction
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_pipeline(model_size: str) -> VoicePipeline:
    # Dynamically update the configuration before initial loading
    settings.WHISPER_MODEL = model_size
    return VoicePipeline()

# (load_tts_generator removed to prevent caching issues)

# -----------------------------------------------------------------------------
# Helper render functions
# -----------------------------------------------------------------------------
def get_language_badge_html(lang_code: str) -> str:
    if lang_code == "hi":
        return '<span class="badge badge-hi">Hindi</span>'
    elif lang_code == "en":
        return '<span class="badge badge-en">English</span>'
    elif lang_code == "gu":
        return '<span class="badge badge-gu">Gujarati</span>'
    else:
        return f'<span class="badge" style="background-color:#757575;">{lang_code.upper()}</span>'

def get_noise_level_html(level: str) -> str:
    if level == "N/A":
        return '<span style="font-size: 12px; color: gray; vertical-align: middle;">⌨ Keyboard Input</span>'
    color = "green" if level == "low" else "orange" if level == "medium" else "red"
    return f'<span class="noise-dot" style="color: {color};">●</span> <span style="font-size: 12px; color: gray; vertical-align: middle;">{level.capitalize()} Noise</span>'

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "latest_error" not in st.session_state:
    st.session_state.latest_error = None
if "recording" not in st.session_state:
    st.session_state.recording = False
if "recorder" not in st.session_state:
    st.session_state.recorder = None



# Sidebar layout
st.sidebar.title("⚙ Settings")

model_size = st.sidebar.selectbox(
    "Whisper Model Size",
    options=["tiny", "small", "medium", "large-v2"],
    index=2,  # default to 'medium'
    help="Select the speech-to-text model size. Larger models are slower but more accurate."
)

ptt_mode = st.sidebar.radio(
    "Recording Mode",
    options=["Auto detect silence", "Push to talk"],
    help="Auto detect silence will stop when you pause. Push to talk records for a fixed duration."
)

ptt_duration = 5
if ptt_mode == "Push to talk":
    ptt_duration = st.sidebar.slider(
        "Recording Duration (seconds)",
        min_value=3,
        max_value=15,
        value=5
    )

# Load TTS Generator and available system voices directly (uncached)
voice_synthesizer = TTSGenerator()
available_voices = []
try:
    available_voices = voice_synthesizer.get_available_voices()
except Exception as tts_err:
    st.sidebar.error(f"SAPI5 init error: {tts_err}")
    import traceback
    st.sidebar.code(traceback.format_exc())

st.sidebar.divider()
st.sidebar.subheader("🔊 Text-To-Speech (TTS)")

enable_tts = st.sidebar.checkbox(
    "Enable Voice Response (TTS)",
    value=True,
    help="Assistant responses will be spoken back to you in English."
)

selected_voice_name = "None"
selected_voice_id = None
tts_rate = 200
tts_volume = 1.0

if enable_tts and available_voices:
    voice_options = {voice["name"]: voice["id"] for voice in available_voices}
    selected_voice_name = st.sidebar.selectbox(
        "Assistant Voice",
        options=list(voice_options.keys()),
        index=0
    )
    selected_voice_id = voice_options[selected_voice_name]
    
    tts_rate = st.sidebar.slider(
        "Speech Speed (Rate)",
        min_value=100,
        max_value=300,
        value=200,
        step=10,
        help="Adjust the speech pace. Standard is 200."
    )
    
    tts_volume = st.sidebar.slider(
        "Voice Volume",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.1
    )

st.sidebar.divider()

# Interactive utilities
if st.sidebar.button("🗑 Clear Chat History", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.latest_error = None
    st.rerun()

st.sidebar.info("🔒 All processing happens locally. Speech transcription and translation models run on CPU, while Chat responds via a local Ollama server.")

# Main area title
st.title("Vaani 🎙")
st.markdown("##### Speak in Hindi, English, or Gujarati to chat with your local AI assistant")

# Display the conversation history bubbles
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display translation diagnostics under user speech bubble
        if message["role"] == "user" and "metadata" in message:
            meta = message["metadata"]
            lang_badge = get_language_badge_html(meta["detected_language"])
            noise_dot = get_noise_level_html(meta["noise_level"])
            
            st.markdown(
                f"<div style='margin-top: 6px; padding: 4px 8px; background: rgba(150, 150, 150, 0.05); border-radius: 6px; font-size: 12px; color: gray;'>"
                f"{lang_badge} {noise_dot} | <i>Original: \"{meta['original_text']}\"</i> | Confidence: {meta['confidence']:.1%}"
                f"</div>",
                unsafe_allow_html=True
            )
        elif message["role"] == "assistant" and message.get("tts_audio") is not None:
            st.audio(message["tts_audio"], format="audio/wav", autoplay=False)

# Input container displaying error if any
if st.session_state.latest_error:
    st.error(f"⚠️ Error: {st.session_state.latest_error}")
    if st.button("Dismiss", use_container_width=True):
        st.session_state.latest_error = None
        st.rerun()

# Anchor mic button above the native chat input at the bottom
st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
col_spacer, col_mic = st.columns([0.88, 0.12])
with col_mic:
    if st.session_state.recording:
        mic_clicked = st.button("⏹ Stop", key="voice_mic_btn", use_container_width=True, type="primary", help="Stop recording and process audio")
    else:
        mic_clicked = st.button("🎙", key="voice_mic_btn", use_container_width=True, type="secondary", help="Record voice input")

# Native standard chat input box
user_typed_input = st.chat_input("Message Vaani...")

# Handle Start/Stop click events
if mic_clicked:
    st.session_state.latest_error = None
    if not st.session_state.recording:
        # Start background recording
        st.session_state.recording = True
        duration = ptt_duration if ptt_mode == "Push to talk" else None
        st.session_state.recorder = ThreadedRecorder(duration_seconds=duration)
        st.session_state.recorder.start()
        st.rerun()
    else:
        # Stop background recording manually
        st.session_state.recording = False
        st.rerun()

# If recording is active, poll the recorder state
if st.session_state.recording:
    st.info("🎙 Listening... Speak now. Click the ⏹ Stop button when done.")
    while st.session_state.recording:
        if st.session_state.recorder and st.session_state.recorder.is_finished():
            # Stopped automatically (silence detected or max recording timeout reached)
            st.session_state.recording = False
            st.rerun()
        time.sleep(0.1)

# Handle Voice Input processing when recording has finished and a recorder exists
audio = None
silence_audio = None
if not st.session_state.recording and st.session_state.recorder is not None:
    with st.spinner("⚙ Processing speech & generating reply..."):
        try:
            audio, silence_audio = st.session_state.recorder.stop()
        except Exception as e:
            st.session_state.latest_error = f"Audio Capture Failed: {e}"
        finally:
            st.session_state.recorder = None

    if audio is not None:
        try:
            # Load cached model pipeline
            pipeline = load_pipeline(model_size)
            if not hasattr(pipeline, "response_generator"):
                st.cache_resource.clear()
                pipeline = load_pipeline(model_size)

            # Estimate noise and clean
            noise_level = estimate_noise_level(audio)
            audio_cleaned = reduce_noise(audio, settings.SAMPLE_RATE, silence_audio=silence_audio)

            # Transcribe
            transcribe_result = pipeline.stt_engine.transcribe(audio_cleaned)
            original_text = transcribe_result["text"]
            detected_lang = transcribe_result["language"]
            confidence = transcribe_result["confidence"]

            # Translate
            if detected_lang == "en":
                english_text = original_text
            else:
                english_text = pipeline.translation_engine.translate_mixed(original_text)

            # Format chat payload to submit to Ollama
            payload_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.chat_history
            ]
            
            # Append the newly translated user query to the history
            payload = payload_history + [{"role": "user", "content": english_text}]

            # Construct metadata dictionary
            metadata = {
                "original_text": original_text,
                "detected_language": detected_lang,
                "confidence": confidence,
                "noise_level": noise_level
            }

            # Save user prompt to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": english_text,
                "metadata": metadata
            })

            # Stream response dynamically in the UI
            with st.chat_message("user"):
                st.markdown(english_text)
                lang_badge = get_language_badge_html(detected_lang)
                noise_dot = get_noise_level_html(noise_level)
                st.markdown(
                    f"<div style='margin-top: 6px; padding: 4px 8px; background: rgba(150, 150, 150, 0.05); border-radius: 6px; font-size: 12px; color: gray;'>"
                    f"{lang_badge} {noise_dot} | <i>Original: \"{original_text}\"</i> | Confidence: {confidence:.1%}"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with st.chat_message("assistant"):
                llm_response = st.write_stream(pipeline.response_generator.generate_response_stream(payload))
                
                tts_bytes = None
                if enable_tts:
                    try:
                        tts_bytes = voice_synthesizer.generate_speech(
                            llm_response,
                            voice_id=selected_voice_id,
                            rate=tts_rate,
                            volume=tts_volume
                        )
                        st.audio(tts_bytes, format="audio/wav", autoplay=True)
                    except Exception as tts_err:
                        st.warning(f"Voice generation failed: {tts_err}")

            # Save model response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": llm_response,
                "tts_audio": tts_bytes
            })
            st.rerun()

        except Exception as e:
            st.session_state.latest_error = str(e)
            st.rerun()

# Handle Typed Chat Input
if user_typed_input:
    st.session_state.latest_error = None

    with st.spinner("⚙ Processing text & generating reply..."):
        try:
            # Load cached model pipeline
            pipeline = load_pipeline(model_size)
            if not hasattr(pipeline, "response_generator"):
                st.cache_resource.clear()
                pipeline = load_pipeline(model_size)

            # Detect language of the input text
            try:
                from langdetect import detect
                detected_lang = detect(user_typed_input)
            except Exception:
                detected_lang = "en"
            
            # Script-based fallback for language routing
            is_gujarati = any(ord(c) in range(0x0A80, 0x0AFF) for c in user_typed_input)
            is_devanagari = any(ord(c) in range(0x0900, 0x097F) for c in user_typed_input)
            if is_gujarati:
                detected_lang = "gu"
            elif is_devanagari:
                detected_lang = "hi"
            elif detected_lang not in ["hi", "gu", "en"]:
                detected_lang = "en"

            # Translate
            if detected_lang == "en":
                english_text = user_typed_input
            else:
                english_text = pipeline.translation_engine.translate_mixed(user_typed_input)

            # Format chat payload to submit to Ollama
            payload_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.chat_history
            ]
            
            # Append the newly translated user query to the history
            payload = payload_history + [{"role": "user", "content": english_text}]

            # Construct metadata dictionary for keyboard input
            metadata = {
                "original_text": user_typed_input,
                "detected_language": detected_lang,
                "confidence": 1.0,
                "noise_level": "N/A"
            }

            # Save user prompt to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": english_text,
                "metadata": metadata
            })

            # Stream response dynamically in the UI
            with st.chat_message("user"):
                st.markdown(english_text)
                lang_badge = get_language_badge_html(detected_lang)
                noise_dot = get_noise_level_html("N/A")
                st.markdown(
                    f"<div style='margin-top: 6px; padding: 4px 8px; background: rgba(150, 150, 150, 0.05); border-radius: 6px; font-size: 12px; color: gray;'>"
                    f"{lang_badge} {noise_dot} | <i>Original: \"{user_typed_input}\"</i> | Confidence: 100.0%"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with st.chat_message("assistant"):
                llm_response = st.write_stream(pipeline.response_generator.generate_response_stream(payload))
                
                tts_bytes = None
                if enable_tts:
                    try:
                        tts_bytes = voice_synthesizer.generate_speech(
                            llm_response,
                            voice_id=selected_voice_id,
                            rate=tts_rate,
                            volume=tts_volume
                        )
                        st.audio(tts_bytes, format="audio/wav", autoplay=True)
                    except Exception as tts_err:
                        st.warning(f"Voice generation failed: {tts_err}")

            # Save model response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": llm_response,
                "tts_audio": tts_bytes
            })
            st.rerun()

        except Exception as e:
            st.session_state.latest_error = str(e)
            st.rerun()
