import numpy as np
import noisereduce as nr

def reduce_noise(audio: np.ndarray, sample_rate: int, silence_audio: np.ndarray = None) -> np.ndarray:
    """
    Reduces noise in the given float32 audio array. Uses the provided silence_audio
    as the noise profile. If not provided, falls back to using the first 0.5 seconds of the audio.
    """
    if silence_audio is not None and len(silence_audio) > 0:
        y_noise = silence_audio
    else:
        # Calculate samples corresponding to the first 0.5 seconds of audio
        num_noise_samples = int(0.5 * sample_rate)
        if len(audio) <= num_noise_samples:
            # Fall back to using the entire audio clip if it's shorter than 0.5 seconds
            y_noise = audio
        else:
            y_noise = audio[:num_noise_samples]

    # Run noisereduce with 80% strength reduction to maintain voice naturalness
    cleaned_audio = nr.reduce_noise(
        y=audio,
        sr=sample_rate,
        y_noise=y_noise,
        prop_decrease=0.8
    )
    
    return cleaned_audio.astype(np.float32)


def estimate_noise_level(audio: np.ndarray) -> str:
    """
    Estimates noise level by calculating the Root Mean Square (RMS) of the audio array.
    Categorizes the result as 'low', 'medium', or 'high'.
    """
    if len(audio) == 0:
        return "low"
        
    # Calculate Root Mean Square
    rms = np.sqrt(np.mean(np.square(audio)))
    
    if rms < 0.02:
        return "low"
    elif rms < 0.06:
        return "medium"
    else:
        return "high"
