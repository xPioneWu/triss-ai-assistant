"""
env_loader.py  —  .env dosyasını yükler
main.py ve triss_core.py'den önce import edilmeli.
"""

import os
from pathlib import Path


def load():
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return

    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        # python-dotenv yoksa manuel oku
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


load()
