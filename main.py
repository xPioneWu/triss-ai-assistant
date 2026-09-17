import env_loader
import threading
import sys
import logging
from triss_core import TrissAssistant

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("triss.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("Triss")


def text_input_loop(triss):
    while triss.running:
        try:
            sys.stdout.write("Yaz > ")
            sys.stdout.flush()
            text = sys.stdin.readline().strip()
            if not text:
                continue
            log.info(f"[Yazildi] {text}")
            triss._handle_input(text)
        except EOFError:
            break
        except KeyboardInterrupt:
            break


def main():
    print("Triss baslatiliyor...")
    triss = TrissAssistant()

    listen_thread = threading.Thread(target=triss.listen_loop, daemon=True)
    listen_thread.start()

    log.info("Hazir! 'gunaydın triss' yazarak veya soyleyerek baslatın.")

    try:
        text_input_loop(triss)
    except KeyboardInterrupt:
        pass
    finally:
        triss.shutdown()
        print("Gorusuruz!")
        sys.exit(0)


if __name__ == "__main__":
    main()