"""Entry point for python -m motd_gen."""

import sys
import threading
import time
import os
from pathlib import Path
from motd_gen.engine import build_motd

DEFAULT_CONFIG = Path(__file__).parent.parent / "config" / "motd.json"

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def spinner(stop_event: threading.Event) -> None:
    """Animate a spinner until stop_event is set."""
    i = 0
    while not stop_event.is_set():
        frame = SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
        sys.stdout.write(f"\r  {frame} Loading MOTD...")
        sys.stdout.flush()
        i += 1
        stop_event.wait(0.08)

    # Clear the spinner line
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()


def main() -> None:
    """Run the MOTD generator."""
    config_path = str(DEFAULT_CONFIG)

    os.system("clear")

    stop_event = threading.Event()
    spin_thread = threading.Thread(target=spinner, args=(stop_event,), daemon=True)
    spin_thread.start()

    motd = build_motd(config_path)

    stop_event.set()
    spin_thread.join()

    print(motd)


if __name__ == "__main__":
    main()