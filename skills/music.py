"""
skills/music.py  —  Spotify müzik kontrolü (spotipy)
"""

import os
import logging
import subprocess
import time

log = logging.getLogger("Triss.Music")

# Spotify API kimlik bilgileri (.env'den okunur)
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI  = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")


class MusicController:
    def __init__(self):
        self.sp = None
        self._init_spotify()

    def _init_spotify(self):
        """Spotify bağlantısını kur."""
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            log.warning("Spotify API anahtarları eksik. Müzik kontrolü devre dışı.")
            return

        try:
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth

            scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing"

            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET,
                    redirect_uri=SPOTIFY_REDIRECT_URI,
                    scope=scope,
                    cache_path=".spotify_cache",
                    open_browser=True,
                )
            )
            log.info("Spotify bağlantısı kuruldu.")
        except ImportError:
            log.warning("spotipy yüklü değil. pip install spotipy")
        except Exception as e:
            log.error(f"Spotify başlatılamadı: {e}")

    def _get_active_device(self):
        """Aktif Spotify cihazını bul."""
        if not self.sp:
            return None
        try:
            devices = self.sp.devices()
            for d in devices.get("devices", []):
                if d["is_active"]:
                    return d["id"]
            # Aktif yoksa ilkini al
            devs = devices.get("devices", [])
            if devs:
                return devs[0]["id"]
        except Exception as e:
            log.error(f"Cihaz alınamadı: {e}")
        return None

    def _ensure_spotify_open(self):
        """Spotify uygulaması kapalıysa aç."""
        try:
            subprocess.Popen(
                ["spotify"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
            )
            time.sleep(3)
        except Exception:
            pass

    def play(self, query: str) -> str:
        """Şarkı veya sanatçı ara ve çal."""
        if not self.sp:
            return self._no_spotify_msg()

        try:
            self._ensure_spotify_open()
            device_id = self._get_active_device()

            if not device_id:
                return "Aktif bir Spotify cihazı bulunamadı. Lütfen Spotify'ı açın."

            # Ara
            results = self.sp.search(q=query, type="track,artist", limit=5)

            tracks = results.get("tracks", {}).get("items", [])
            if not tracks:
                return f"Üzgünüm, '{query}' için bir şey bulamadım."

            track    = tracks[0]
            track_uri = track["uri"]
            name     = track["name"]
            artist   = track["artists"][0]["name"]

            self.sp.start_playback(device_id=device_id, uris=[track_uri])
            return f"{artist} - {name} çalıyor."

        except Exception as e:
            log.error(f"Müzik çalınamadı: {e}")
            return "Müziği çalarken bir hata oluştu."

    def stop(self) -> str:
        """Müziği durdur."""
        if not self.sp:
            return self._no_spotify_msg()
        try:
            self.sp.pause_playback()
            return "Müzik durduruldu."
        except Exception:
            return "Müzik zaten durmuş."

    def next_track(self) -> str:
        """Sonraki şarkıya geç."""
        if not self.sp:
            return self._no_spotify_msg()
        try:
            self.sp.next_track()
            time.sleep(0.5)
            current = self.sp.current_playback()
            if current and current.get("item"):
                name   = current["item"]["name"]
                artist = current["item"]["artists"][0]["name"]
                return f"Sonraki şarkı: {artist} - {name}."
            return "Sonraki şarkıya geçildi."
        except Exception as e:
            log.error(f"Sonraki şarkı hatası: {e}")
            return "Şarkı geçilemedi."

    def _no_spotify_msg(self) -> str:
        return (
            "Spotify kontrolü için API anahtarları gerekiyor. "
            "Lütfen setup.py dosyasını çalıştırın."
        )
