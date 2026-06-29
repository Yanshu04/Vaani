import pytest
import sys
from app.core.voice_synthesizer import TTSGenerator

def test_get_available_voices():
    generator = TTSGenerator()
    voices = generator.get_available_voices()
    
    assert len(voices) > 0
    # The first voice should be an Edge voice
    assert voices[0]["type"] == "edge"
    # Ensure all required keys exist
    for v in voices:
        assert "id" in v
        assert "name" in v
        assert "gender" in v
        assert "languages" in v
        assert "type" in v

def test_generate_speech_edge():
    generator = TTSGenerator()
    # Test using one of our premium Edge voices (should fetch online or fallback)
    audio_bytes = generator.generate_speech("Hello, this is a test.", voice_id="en-US-AvaNeural")
    assert len(audio_bytes) > 0
    
    # If online, it's MP3 (no RIFF header). If offline fallback to SAPI5, it's WAV (starts with RIFF)
    # In both cases, valid audio data is returned.
    assert isinstance(audio_bytes, bytes)

def test_generate_speech_sapi5():
    if sys.platform != "win32":
        pytest.skip("SAPI5 tests only run on Windows")
        
    generator = TTSGenerator()
    voices = generator.get_available_voices()
    sapi5_voices = [v for v in voices if v["type"] == "sapi5"]
    
    if not sapi5_voices:
        pytest.skip("No SAPI5 voices found on this machine")
        
    sapi5_voice_id = sapi5_voices[0]["id"]
    audio_bytes = generator.generate_speech("Hello, SAPI5 offline fallback test.", voice_id=sapi5_voice_id)
    assert len(audio_bytes) > 0
    assert audio_bytes.startswith(b"RIFF")  # WAV format
