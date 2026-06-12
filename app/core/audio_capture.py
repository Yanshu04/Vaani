import time
import numpy as np
import sounddevice as sd
import webrtcvad
from app.config import settings

def record_until_silence() -> tuple[np.ndarray, np.ndarray | None]:
    """
    Records audio from the microphone and stops automatically when silence is detected
    or when the hard cap MAX_RECORD_SECONDS is reached.
    Returns a tuple of (audio_float32, silence_float32) where silence_float32 contains
    only non-speech frames for noise profile estimation.
    """
    sample_rate = settings.SAMPLE_RATE
    vad_aggressiveness = settings.VAD_AGGRESSIVENESS
    silence_ms = settings.SILENCE_MS
    max_record_seconds = settings.MAX_RECORD_SECONDS

    # webrtcvad requires 10, 20, or 30ms frames. We use 30ms.
    frame_duration_ms = 30
    frame_size = int(sample_rate * (frame_duration_ms / 1000.0))  # 480 samples

    try:
        vad = webrtcvad.Vad(vad_aggressiveness)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize VAD: {e}")

    audio_frames = []
    silence_frames = []
    
    # Silence tracking limits
    max_silence_frames = silence_ms // frame_duration_ms
    max_total_frames = int((max_record_seconds * 1000) / frame_duration_ms)

    consecutive_silence_frames = 0
    total_frames = 0
    speech_detected_ever = False

    try:
        # Open mono input stream using 16-bit PCM format
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
            print("Listening... Speak now.")
            while total_frames < max_total_frames:
                frame, overflowed = stream.read(frame_size)
                if len(frame) == 0:
                    continue

                frame_flat = frame.flatten()
                frame_bytes = frame_flat.tobytes()

                # VAD operates on 16-bit raw PCM bytes
                is_speech = vad.is_speech(frame_bytes, sample_rate)

                audio_frames.append(frame_flat)
                if not is_speech:
                    silence_frames.append(frame_flat)

                total_frames += 1

                if is_speech:
                    speech_detected_ever = True
                    consecutive_silence_frames = 0
                else:
                    if speech_detected_ever:
                        consecutive_silence_frames += 1
                        if consecutive_silence_frames >= max_silence_frames:
                            print("Silence detected. Stopping recording.")
                            break
    except sd.PortAudioError as e:
        raise RuntimeError("Microphone not found or permission denied") from e

    if not audio_frames:
        raise ValueError("No audio captured")

    audio_data = np.concatenate(audio_frames)

    if not speech_detected_ever:
        raise ValueError("No speech detected, please try again")

    # Normalize int16 -> float32 range [-1.0, 1.0]
    audio_float32 = audio_data.astype(np.float32) / 32768.0

    silence_float32 = None
    if silence_frames:
        silence_data = np.concatenate(silence_frames)
        silence_float32 = silence_data.astype(np.float32) / 32768.0

    return audio_float32, silence_float32


def push_to_talk_record(duration_seconds: int = 5) -> tuple[np.ndarray, np.ndarray | None]:
    """
    Records audio from the microphone for a fixed duration, displaying a countdown.
    Returns a tuple of (audio_float32, silence_float32) where silence_float32 contains
    only non-speech frames for noise profile estimation.
    """
    sample_rate = settings.SAMPLE_RATE
    audio_list = []

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
            print(f"Recording for {duration_seconds} seconds...")
            for remaining in range(duration_seconds, 0, -1):
                print(f"Recording... {remaining} seconds remaining")
                # Read 1 second worth of audio samples
                chunk, overflowed = stream.read(sample_rate)
                audio_list.append(chunk.flatten())
    except sd.PortAudioError as e:
        raise RuntimeError("Microphone not found or permission denied") from e

    if not audio_list:
        raise ValueError("No audio captured")

    audio_data = np.concatenate(audio_list)

    # Perform VAD validation to verify speech is present
    vad = webrtcvad.Vad(settings.VAD_AGGRESSIVENESS)
    frame_duration_ms = 30
    frame_size = int(sample_rate * (frame_duration_ms / 1000.0))

    speech_detected = False
    silence_frames = []
    for i in range(0, len(audio_data) - frame_size, frame_size):
        frame = audio_data[i : i + frame_size]
        frame_bytes = frame.tobytes()
        if len(frame_bytes) == frame_size * 2:  # 2 bytes per int16 sample
            if vad.is_speech(frame_bytes, sample_rate):
                speech_detected = True
            else:
                silence_frames.append(frame)

    if not speech_detected:
        raise ValueError("No speech detected, please try again")

    audio_float32 = audio_data.astype(np.float32) / 32768.0

    silence_float32 = None
    if silence_frames:
        silence_data = np.concatenate(silence_frames)
        silence_float32 = silence_data.astype(np.float32) / 32768.0

    return audio_float32, silence_float32
