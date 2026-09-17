"""
voice_output.py  —  Cevap çıkışı.

Varsayılan olarak yazili modda calisir (TRISS_TEXT_ONLY=1).
TRISS_TEXT_ONLY=0 oldugunda edge-tts ile sesli cikis dener.
"""

import asyncio
import logging
import os
import tempfile
import threading

log = logging.getLogger("Triss.Voice")

# Microsoft Edge TTS - Türkçe kadın sesi
# Seçenekler: tr-TR-EmelNeural (sıcak), tr-TR-AhmetNeural (erkek)
VOICE = "tr-TR-EmelNeural"
RATE  = "+5%"    # konuşma hızı
PITCH = "+0Hz"   # ses tonu
TEXT_ONLY_ENV = "TRISS_TEXT_ONLY"


def _text_only_mode() -> bool:
    """Yazili cevap modunu ortam degiskeninden okur."""
    val = os.getenv(TEXT_ONLY_ENV, "1").strip().lower()
    return val not in {"0", "false", "no", "off"}


async def _synthesize(text: str, output_path: str):
    """edge-tts ile ses dosyası oluştur."""
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(output_path)


def _play_audio(path: str):
    """Windows'ta ses dosyasını çal."""
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
    except ImportError:
        # pygame yoksa playsound dene
        try:
            from playsound import playsound
            playsound(path)
        except ImportError:
            # Son çare: Windows winsound
            import subprocess
            subprocess.run(
                ["powershell", "-c", f'(New-Object Media.SoundPlayer "{path}").PlaySync()'],
                check=True,
                capture_output=True,
            )


def speak_sync(text: str):
    """Senkron cikis: yazili veya sesli."""
    if not text or not text.strip():
        return

    # Faz 0-4: varsayilan olarak sadece yazili cevap.
    if _text_only_mode():
        print(f"[Triss]: {text}")
        log.info(f"[TEXT] {text}")
        return

    log.info(f"[TTS] {text}")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    try:
        asyncio.run(_synthesize(text, tmp_path))
        _play_audio(tmp_path)
    except Exception as e:
        log.error(f"TTS hatası: {e}")
        print(f"[Triss]: {text}")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def speak(text: str):
    """Asenkron cikis."""
    if _text_only_mode():
        speak_sync(text)
        return

    t = threading.Thread(target=speak_sync, args=(text,), daemon=True)
    t.start()
