import pyttsx3
import threading
import tempfile
import os
import ctypes

def run_in_sta_thread(func):
    """
    Decorator/wrapper to execute pyttsx3 operations on a clean STA thread.
    This resolves SAPI5 COM threading mode conflicts (MTA vs STA) inside Streamlit worker threads.
    """
    def wrapper(*args, **kwargs):
        result = []
        error = []
        
        def target():
            try:
                # Initialize COM as STA (Single Threaded Apartment) on this fresh thread
                ctypes.windll.ole32.CoInitialize(None)
                res = func(*args, **kwargs)
                result.append(res)
            except Exception as e:
                import traceback
                traceback.print_exc()
                error.append(e)
            finally:
                try:
                    ctypes.windll.ole32.CoUninitialize()
                except Exception:
                    pass

        t = threading.Thread(target=target)
        t.start()
        t.join()
        
        if error:
            raise error[0]
        return result[0] if result else None
    return wrapper

class TTSGenerator:
    """
    Offline Text-to-Speech generator utilizing pyttsx3.
    Executes SAPI5 queries and speech generation inside custom STA threads to prevent Streamlit COM errors.
    """
    def __init__(self):
        pass

    @run_in_sta_thread
    def get_available_voices(self) -> list[dict]:
        """
        Dynamically query available voice options installed on the host OS.
        """
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        voice_list = []
        for voice in voices:
            voice_list.append({
                "id": voice.id,
                "name": voice.name,
                "gender": voice.gender,
                "languages": voice.languages
            })
        return voice_list

    @run_in_sta_thread
    def generate_speech_to_file(self, text: str, voice_id: str, rate: int, volume: float, temp_file: str):
        """
        Synthesizes text and saves it directly to a temporary file. Must run inside STA thread.
        """
        engine = pyttsx3.init()
        if voice_id:
            engine.setProperty('voice', voice_id)
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        
        engine.save_to_file(text, temp_file)
        engine.runAndWait()

    def generate_speech(self, text: str, voice_id: str = None, rate: int = 200, volume: float = 1.0) -> bytes:
        """
        Synthesize text into WAV audio bytes offline.
        Uses generate_speech_to_file running in a clean STA thread, then reads the output file.
        """
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, next(tempfile._get_candidate_names()) + ".wav")
        
        try:
            self.generate_speech_to_file(text, voice_id, rate, volume, temp_file)
            
            # Retrieve generated audio bytes and clean up
            if os.path.exists(temp_file):
                with open(temp_file, "rb") as f:
                    audio_bytes = f.read()
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
                return audio_bytes
            else:
                raise FileNotFoundError(f"TTS output file not found: {temp_file}")
        except Exception as e:
            # Clean up if temp file was left behind
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            raise RuntimeError(f"Offline TTS generation failed: {e}")
