import json
import os
import logging
import speech_recognition as sr
import ollama

from voice_output import speak, speak_sync
from skills.weather import get_weather
from skills.music import MusicController
from skills.system import SystemController

log = logging.getLogger("Triss.Core")

OLLAMA_MODEL  = "llama3.2"
WAKE_WORD_ON  = ["gunaydın triss", "gunaydin triss", "merhaba triss"]
WAKE_WORD_OFF = ["iyi geceler triss", "iyi geceler", "hosca kal triss"]

MEMORY_FILE = "memory.json"
MAX_HISTORY = 20

SYSTEM_PROMPT = """Sen Triss adinda, Turkce konusan, zeki ve sicak bir sesli AI asistansin.
Kullanicinin kisisel masaustu asistanisin. Triss, Witcher oyunundaki buyucu karakterin adidir.

KURALLAR:
- Her zaman Turkce cevap ver.
- Cevaplarin kisa ve sesli okumaya uygun olsun.
- Kullaniciyla samimi ol.

KOMUT formati (sadece bu komutlari tanıdigında JSON dondur, yoksa normal cevap ver):
- Muzik calmak icin: {"action": "play_music", "query": "<sarki/sanatci adi>"}
- Muzigi durdurmak icin: {"action": "stop_music"}
- Muzigi atlamak icin: {"action": "next_music"}
- Hava durumu icin: {"action": "weather", "city": "<sehir>"}
- Uygulama acmak icin: {"action": "open_app", "app": "<uygulama adi>"}
- Webde aramak icin: {"action": "web_search", "query": "<arama terimi>"}

Eger kullanici bu komutlardan birini istiyorsa SADECE JSON dondur.
Aksi halde normal, sicak ve kisa bir Turkce cevap ver."""


class TrissAssistant:
    def __init__(self):
        self._check_ollama()
        self.music   = MusicController()
        self.system  = SystemController()
        self.history = self._load_history()
        self.active  = False
        self.running = True

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold         = 150
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold          = 0.8

        log.info(f"Triss Core baslatildi. LLM modeli: {OLLAMA_MODEL}")

    def _check_ollama(self):
        try:
            ollama.list()
            log.info(f"Ollama baglantisi basarili. Model: {OLLAMA_MODEL}")
        except Exception as e:
            log.error(f"Ollama servisine baglanilamadi: {e}")
            raise RuntimeError(f"Ollama servisine baglanilamadi! Lutfen Ollama'nin calistigindan emin olun: {e}")

    def listen_loop(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            log.info("Mikrofon dinleniyor...")

            while self.running:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    text  = self._transcribe(audio)
                    if not text:
                        continue
                    log.info(f"[Duyuldu] {text}")
                    self._handle_input(text)
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    log.error(f"Dinleme hatasi: {e}")

    def _handle_input(self, text: str):
        lower = text.lower().strip()

        if not self.active:
            wake = any(w in lower for w in WAKE_WORD_ON)
            triss_benzeri = any(x in lower for x in ["tris", "trees", "triss", "trish"])
            gunaydın = any(x in lower for x in ["gunaydın", "gunaydin", "merhaba", "hey"])
            if wake or (gunaydın and triss_benzeri):
                self._wake_up()
            return

        kapat = any(w in lower for w in WAKE_WORD_OFF)
        triss_benzeri = any(x in lower for x in ["tris", "trees", "triss", "trish"])
        gece = any(x in lower for x in ["iyi geceler", "hosca kal", "gorusuruz"])
        if kapat or (gece and triss_benzeri):
            self._sleep()
            return

        self._process_command(text)

    def _wake_up(self):
        self.active = True
        log.info("Triss UYANIK")
        speak_sync("Merhaba! Sizi duyuyorum, nasil yardimci olabilirim?")

    def _sleep(self):
        self.active = False
        log.info("Triss UYUYOR")
        speak_sync("Iyi geceler! Dinlenin guzelce.")
        self._save_history()

    def _process_command(self, user_text: str):
        self.history.append({"role": "user", "content": user_text})

        if len(self.history) > MAX_HISTORY * 2:
            self.history = self.history[-MAX_HISTORY * 2:]

        try:
            reply = self._generate_reply()
        except Exception as e:
            log.error(f"Ollama hatasi: {e}")
            speak_sync("Uzgunum, su an dusünemiyorum.")
            return

        self.history.append({"role": "assistant", "content": reply})
        log.info(f"[Triss] {reply}")

        if reply.startswith("{"):
            self._execute_skill(reply, user_text)
        else:
            speak(reply)

    def _generate_reply(self) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
        )
        content = response.get("message", {}).get("content", "").strip()
        if not content:
            raise RuntimeError("Ollama bos yanit dondurdu.")
        return content

    def _execute_skill(self, json_str: str, original_text: str):
        try:
            cmd = json.loads(json_str)
        except json.JSONDecodeError:
            speak(json_str)
            return

        action = cmd.get("action", "")
        if action == "play_music":
            speak(self.music.play(cmd.get("query", "")))
        elif action == "stop_music":
            speak(self.music.stop())
        elif action == "next_music":
            speak(self.music.next_track())
        elif action == "weather":
            speak(get_weather(cmd.get("city", "Istanbul")))
        elif action == "open_app":
            speak(self.system.open_app(cmd.get("app", "")))
        elif action == "web_search":
            speak(self.system.web_search(cmd.get("query", "")))
        else:
            speak("Bu komutu henuz ogrenemedim!")

    def _transcribe(self, audio) -> str:
        # Hem wake word (uyandirma) hem de aktif konusma icin yerel Whisper kullanilir
        try:
            import whisper
            import numpy as np
            import io, soundfile as sf

            raw = audio.get_wav_data()
            data, samplerate = sf.read(io.BytesIO(raw))
            if data.ndim > 1:
                data = data[:, 0]
            data = data.astype(np.float32)
            model = _get_whisper_model()
            result = model.transcribe(
                data,
                language="tr",
                initial_prompt="Triss adli sesli asistan.",
            )
            return result["text"].strip()

        except sr.UnknownValueError:
            return ""
        except Exception as e:
            log.debug(f"Transkripsiyon hatasi: {e}")
            return ""

    def _load_history(self) -> list:
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_history(self):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history[-MAX_HISTORY * 2:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Hafiza kaydedilemedi: {e}")

    def shutdown(self):
        self.running = False
        self._save_history()


_whisper_model = None

def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        log.info("Whisper modeli yukleniyor (medium)...")
        _whisper_model = whisper.load_model("medium")
    return _whisper_model