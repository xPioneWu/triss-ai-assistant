"""
setup.py  —  Triss kurulum sihirbazı
Tüm API anahtarlarını toplar ve .env dosyasına yazar.
"""

import os
import sys
import subprocess


BANNER = """
╔══════════════════════════════════════════════╗
║         🔧  Triss Kurulum Sihirbazı          ║
╚══════════════════════════════════════════════╝
"""

ENV_TEMPLATE = """\
# Triss Ortam Değişkenleri
# Bu dosyayı kimseyle paylaşmayın!

# Anthropic API (zorunlu) - console.anthropic.com
ANTHROPIC_API_KEY={anthropic_key}

# OpenWeatherMap (hava durumu) - openweathermap.org/api
OPENWEATHER_API_KEY={weather_key}

# Spotify (müzik) - developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID={spotify_id}
SPOTIFY_CLIENT_SECRET={spotify_secret}
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
"""

PACKAGES = [
    "anthropic",
    "speechrecognition",
    "pyaudio",
    "edge-tts",
    "pygame",
    "requests",
    "python-dotenv",
    "spotipy",
]

OPTIONAL_PACKAGES = [
    ("openai-whisper", "Whisper (gelişmiş Türkçe ses tanıma, ~150MB)"),
    ("pycaw",          "Ses seviyesi kontrolü"),
]


def ask(prompt: str, default: str = "") -> str:
    if default:
        val = input(f"{prompt} [{default}]: ").strip()
        return val if val else default
    else:
        return input(f"{prompt}: ").strip()


def install_packages():
    print("\n📦 Gerekli paketler yükleniyor...\n")
    for pkg in PACKAGES:
        print(f"  ▶ {pkg}")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg, "-q"],
            check=False,
        )

    print("\n📦 İsteğe bağlı paketler:")
    for pkg, desc in OPTIONAL_PACKAGES:
        choice = ask(f"  {desc} yüklensin mi? (e/h)", "e").lower()
        if choice == "e":
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg, "-q"],
                check=False,
            )


def collect_keys() -> dict:
    print("\n🔑 API Anahtarları\n")
    print("  [1] Anthropic API Anahtarı (ZORUNLU)")
    print("      → console.anthropic.com > API Keys > Create Key\n")
    anthropic_key = ask("  Anthropic API Anahtarı")

    print("\n  [2] OpenWeatherMap API Anahtarı (hava durumu için)")
    print("      → openweathermap.org/api > 'Current Weather Data' ücretsiz tier")
    print("      Boş bırakırsanız hava durumu çalışmaz.\n")
    weather_key = ask("  OpenWeatherMap API Anahtarı (boş bırakabilirsiniz)", "")

    print("\n  [3] Spotify API (müzik kontrolü için)")
    print("      → developer.spotify.com/dashboard > Create App")
    print("      Redirect URI olarak: http://localhost:8888/callback ekleyin")
    print("      Boş bırakırsanız müzik kontrolü çalışmaz.\n")
    spotify_id     = ask("  Spotify Client ID (boş bırakabilirsiniz)", "")
    spotify_secret = ask("  Spotify Client Secret (boş bırakabilirsiniz)", "") if spotify_id else ""

    return {
        "anthropic_key" : anthropic_key,
        "weather_key"   : weather_key,
        "spotify_id"    : spotify_id,
        "spotify_secret": spotify_secret,
    }


def write_env(keys: dict):
    env_content = ENV_TEMPLATE.format(**keys)
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    print("\n✅ .env dosyası oluşturuldu.")


def test_microphone():
    print("\n🎙️  Mikrofon testi...")
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
        print("  ✅ Mikrofon çalışıyor!")
    except Exception as e:
        print(f"  ⚠️  Mikrofon hatası: {e}")
        print("  PyAudio kurulumu için: pip install pyaudio")
        print("  Windows'ta ek olarak: pip install pipwin && pipwin install pyaudio")


def test_tts():
    print("\n🔊 TTS testi (Triss'in sesi duyulacak)...")
    try:
        import asyncio
        import edge_tts
        import tempfile
        import pygame

        async def _test():
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp = f.name
            comm = edge_tts.Communicate("Merhaba! Ben Triss. Kurulum başarılı.", "tr-TR-EmelNeural")
            await comm.save(tmp)
            pygame.mixer.init()
            pygame.mixer.music.load(tmp)
            pygame.mixer.music.play()
            import time
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
            os.unlink(tmp)

        asyncio.run(_test())
        print("  ✅ Ses sistemi çalışıyor!")
    except Exception as e:
        print(f"  ⚠️  TTS hatası: {e}")


def main():
    print(BANNER)

    # 1. Paket kurulumu
    do_install = ask("Gerekli Python paketleri yüklensin mi?", "e").lower()
    if do_install == "e":
        install_packages()

    # 2. API anahtarları
    keys = collect_keys()
    write_env(keys)

    # 3. .env'i yükle
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # 4. Testler
    test_microphone()
    test_tts()

    print("""
╔══════════════════════════════════════════════╗
║           ✅  Kurulum Tamamlandı!            ║
║                                              ║
║  Triss'i başlatmak için:                     ║
║       python main.py                         ║
║                                              ║
║  Sonra söyleyin: "Günaydın Triss"            ║
╚══════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
