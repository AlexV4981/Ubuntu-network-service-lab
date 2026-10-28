import time

from parsers.minecraft import process_minecraft_logs
from parsers.controller import process_controller_db

POLL_INTERVAL = 5


def main():
    print("[INGEST] Service started", flush=True)

    while True:
        try:
            process_minecraft_logs()
            process_controller_db()

        except Exception as e:
            print(f"[INGEST ERROR] {e}", flush=True)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
