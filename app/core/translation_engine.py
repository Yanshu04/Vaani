import os
import re
import torch
from langdetect import detect
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from app.config import settings

# Unified NLLB model config
NLLB_MODEL_NAME = "facebook/nllb-200-distilled-600M"

# Map language codes to NLLB language tags
NLLB_LANG_MAP = {
    "hi": "hin_Deva",
    "gu": "guj_Gujr",
    "en": "eng_Latn"
}

SUPPORTED_TRANSLATION_LANGUAGES = {"hi", "gu"}

class Translator:
    def __init__(self):
        """
        Initializes the translation manager with lazy-loading model config.
        """
        self.model = None
        self.tokenizer = None
        self.device = None

    def _load_model(self):
        """
        Lazy-loads the single unified NLLB-200 model and tokenizer.
        Moves model to CUDA GPU if available.
        """
        if self.model is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            os.makedirs(settings.MODELS_DIR, exist_ok=True)
            print(f"Loading unified NLLB-200 model '{NLLB_MODEL_NAME}' on {self.device}...")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    NLLB_MODEL_NAME,
                    cache_dir=settings.MODELS_DIR
                )
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    NLLB_MODEL_NAME,
                    cache_dir=settings.MODELS_DIR
                ).to(self.device)
                print(f"NLLB-200 model '{NLLB_MODEL_NAME}' loaded successfully.")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load/download translation model '{NLLB_MODEL_NAME}': {e}. "
                    "Ensure models are downloaded via download_models.py or an internet connection is available."
                ) from e

    def translate(self, text: str, source_lang: str) -> str:
        """
        Translates text from the given source language to English.
        If the source language is already English ('en'), returns the text unchanged.
        """
        if not text.strip():
            return ""

        if source_lang == "en":
            return text

        if source_lang not in NLLB_LANG_MAP:
            raise ValueError(f"Unsupported source language for translation: {source_lang}")

        self._load_model()

        try:
            # Set source language on the tokenizer
            self.tokenizer.src_lang = NLLB_LANG_MAP[source_lang]
            
            # Tokenize input text (truncating long inputs to match max model size)
            inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate translation tokens targeting English
            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids("eng_Latn")
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=512
            )
            
            # Decode tokens back to English text
            translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return translated_text.strip()
        except Exception as e:
            raise RuntimeError(f"Translation error from '{source_lang}' to 'en': {e}")

    def translate_mixed(self, text: str) -> str:
        """
        Splits the text into sentences by '. ' and '।' (Hindi full stop).
        Uses langdetect to detect the language of each sentence, translates non-English
        sentences individually, and rejoins them.
        Falls back to translating the entire text if sentence processing fails.
        """
        if not text.strip():
            return ""

        try:
            # Split sentences keeping the punctuation marks
            # Split matches after dot-space or after danda (Hindi full stop)
            sentences = re.split(r'(?<=\. )|(?<=।)', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            translated_sentences = []
            for sentence in sentences:
                try:
                    lang = detect(sentence)
                except Exception:
                    # Fallback to English (as-is) if detection fails
                    lang = "en"

                # Route based on detected language
                if lang == "en":
                    translated = sentence
                elif lang == "gu":
                    translated = self.translate(sentence, "gu")
                else:
                    # If lang is 'hi' or any other code, check character scripts to direct
                    # to the proper translation model.
                    is_gujarati = any(ord(c) in range(0x0A80, 0x0AFF) for c in sentence)
                    is_devanagari = any(ord(c) in range(0x0900, 0x097F) for c in sentence)

                    if is_gujarati:
                        translated = self.translate(sentence, "gu")
                    elif is_devanagari or lang == "hi":
                        translated = self.translate(sentence, "hi")
                    else:
                        # Fallback for English script or unrecognized scripts
                        translated = sentence

                translated_sentences.append(translated)

            return " ".join(translated_sentences)

        except Exception as e:
            print(f"Sentence-level split translation failed ({e}). Translating entire text block.")
            try:
                lang = detect(text)
            except Exception:
                lang = "hi"  # Default fallback language

            if lang == "en":
                return text
            elif lang in SUPPORTED_TRANSLATION_LANGUAGES:
                return self.translate(text, lang)
            else:
                # Script-based routing fallback for the entire block
                if any(ord(c) in range(0x0A80, 0x0AFF) for c in text):
                    return self.translate(text, "gu")
                else:
                    return self.translate(text, "hi")
