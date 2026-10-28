import json
import os
import requests

from paths import STATE_DIR, PROCESSED_DIR
from events import create_event


CONTROLLER_URL = "http://minecraft-controller:5000"

LOG_ROOT = "/mc-logs"

OUTPUT_FILE = PROCESSED_DIR / "minecraft.json"



def get_active_server():

    try:

        response = requests.get(
            f"{CONTROLLER_URL}/active-server",
            timeout=5
        )

        return response.json()


    except Exception as e:

        print(
            f"[MINECRAFT ERROR] Could not get active server: {e}",
            flush=True
        )

        return None



def get_log_path(container):

    return f"{LOG_ROOT}/{container}/latest.log"



def get_state_file(container):

    return STATE_DIR / f"{container}.offset"



def get_offset(container):

    state_file = get_state_file(container)


    if not state_file.exists():

        return 0


    with open(state_file, "r") as f:

        return int(f.read().strip())



def save_offset(container, offset):

    state_file = get_state_file(container)


    with open(state_file, "w") as f:

        f.write(str(offset))



def parse_line(line, server):

    return create_event(

        source="minecraft",

        event_type="log",


        action={

            "name": "minecraft_log",

            "category": "game_event"

        },


        result={

            "status": "observed"

        },


        metadata={

            "server": server,

            "raw": line.strip()

        }

    )



def process_minecraft_logs():


    if not STATE_DIR.exists():

        STATE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )


    if not PROCESSED_DIR.exists():

        PROCESSED_DIR.mkdir(
            parents=True,
            exist_ok=True
        )



    active = get_active_server()



    if not active or not active.get("container"):


        print(
            "[MINECRAFT] No active server",
            flush=True
        )

        return



    container = active["container"]

    server = active["server"]



    log_path = get_log_path(container)



    if not os.path.exists(log_path):


        print(
            f"[MINECRAFT ERROR] Missing log {log_path}",
            flush=True
        )

        return



    offset = get_offset(container)


    current_size = os.path.getsize(log_path)



    # Detect log rotation/reset

    if offset > current_size:


        print(
            "[MINECRAFT] Log rotation detected, resetting offset",
            flush=True
        )


        offset = 0



    print(
        f"[MINECRAFT] Active server: {server}",
        flush=True
    )


    print(
        f"[MINECRAFT] Current offset: {offset}",
        flush=True
    )



    with open(log_path, "r") as f:


        f.seek(offset)


        lines = f.readlines()


        new_offset = f.tell()



    print(
        f"[MINECRAFT] New lines found: {len(lines)}",
        flush=True
    )



    if not lines:

        return



    events = [

        parse_line(
            line,
            server
        )

        for line in lines

    ]



    with open(OUTPUT_FILE, "a") as out:


        for event in events:


            out.write(

                json.dumps(event) + "\n"

            )



    save_offset(

        container,

        new_offset

    )



    print(

        f"[INGEST] Minecraft: {len(events)} events",

        flush=True

    )
