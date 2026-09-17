"""
skills/system.py  —  Sistem komutları (uygulama aç, web ara vb.)
"""

import os
import subprocess
import webbrowser
import logging

log = logging.getLogger("Triss.System")

# Uygulama adı → Windows yürütülebilir eşlemesi
APP_MAP = {
    "chrome"      : "chrome",
    "google chrome": "chrome",
    "firefox"     : "firefox",
    "edge"        : "msedge",
    "not defteri" : "notepad",
    "notepad"     : "notepad",
    "hesap makinesi": "calc",
    "calculator"  : "calc",
    "dosya gezgini": "explorer",
    "explorer"    : "explorer",
    "görev yöneticisi": "taskmgr",
    "word"        : "winword",
    "excel"       : "excel",
    "powerpoint"  : "powerpnt",
    "vscode"      : "code",
    "vs code"     : "code",
    "terminal"    : "cmd",
    "cmd"         : "cmd",
    "powershell"  : "powershell",
    "spotify"     : "spotify",
    "discord"     : "discord",
    "slack"       : "slack",
    "zoom"        : "zoom",
    "telegram"    : "telegram",
    "whatsapp"    : "whatsapp",
    "paint"       : "mspaint",
    "video oynatıcı": "wmplayer",
}


class SystemController:

    def open_app(self, app_name: str) -> str:
        """Uygulamayı aç."""
        key = app_name.lower().strip()
        executable = APP_MAP.get(key, key)  # Eşleme yoksa direkt dene

        try:
            subprocess.Popen(
                executable,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return f"{app_name} açılıyor."
        except Exception as e:
            log.error(f"Uygulama açılamadı [{executable}]: {e}")
            return f"Üzgünüm, {app_name} bulunamadı veya açılamadı."

    def web_search(self, query: str) -> str:
        """Google'da ara."""
        if not query:
            return "Ne aramak istediğinizi söyleyin."
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"{query} için Google'da arama açıldı."

    def get_volume(self) -> int:
        """Sistem ses seviyesini al (0-100)."""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            import math

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            db = volume.GetMasterVolumeLevel()
            # dB → 0-100
            level = int(max(0, min(100, (db + 65) * 100 / 65)))
            return level
        except Exception:
            return -1

    def set_volume(self, level: int) -> str:
        """Ses seviyesini ayarla (0-100)."""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            level = max(0, min(100, level))
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            # 0-100 → dB (-65 to 0)
            db = -65.0 + (level / 100.0) * 65.0
            volume.SetMasterVolumeLevel(db, None)
            return f"Ses seviyesi yüzde {level} olarak ayarlandı."
        except ImportError:
            # pycaw yoksa PowerShell kullan
            subprocess.run(
                ["powershell", "-c", f"(Get-AudioDevice -Playback).Volume = {level}"],
                capture_output=True,
            )
            return f"Ses seviyesi yüzde {level} olarak ayarlandı."
        except Exception as e:
            return f"Ses seviyesi ayarlanamadı: {e}"
