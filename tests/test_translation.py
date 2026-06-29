import pytest
from app.core.translation_engine import Translator

def test_translate_to_lang():
    t = Translator()
    # Translate English to Hindi
    hi_text = t.translate_to_lang("Hello, how are you?", "hi")
    assert len(hi_text.strip()) > 0
    assert any(ord(c) in range(0x0900, 0x097F) for c in hi_text)

    # Translate English to Gujarati
    gu_text = t.translate_to_lang("Hello, how are you?", "gu")
    assert len(gu_text.strip()) > 0
    assert any(ord(c) in range(0x0A80, 0x0AFF) for c in gu_text)

    # Translate English to English
    en_text = t.translate_to_lang("Hello, how are you?", "en")
    assert en_text == "Hello, how are you?"
