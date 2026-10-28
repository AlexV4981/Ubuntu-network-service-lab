import json
from paths import STATE_DIR, PROCESSED_DIR
from events import create_event

DB_PATH = "/controller/data/controller.db"

STATE_FILE = STATE_DIR / "db.offset"
OUTPUT_FILE = PROCESSED_DIR / "controller.json"


import sqlite3


def get_offset():

    if not STATE_FILE.exists():
        return 0

    with open(STATE_FILE, "r") as f:
        return int(f.read().strip())


def save_offset(offset):

    with open(STATE_FILE, "w") as f:
        f.write(str(offset))


def parse_row(row):

    return create_event(
        source="controller",
        event_type="command",

        timestamp=row[1],

        actor={
            "id": row[2],
            "name": row[3]
        },

        action={
            "name": row[4],
            "category": "server_control"
        },

        result={
            "status": row[5]
        },

        metadata={
            "db_id": row[0],
            "previous_state": row[6],
            "new_state": row[7]
        }
    )





def process_controller_db():

    if not STATE_FILE.parent.exists():
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not PROCESSED_DIR.exists():
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


    offset = get_offset()

    print(f"[CONTROLLER] Current offset: {offset}", flush=True)


    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
            id,
            time,
            user_id,
            user,
            command,
            result,
            prior_state,
            new_state

        FROM command_history

        WHERE id > ?

        ORDER BY id ASC
        """,
        (offset,)
    )


    rows = cursor.fetchall()

    conn.close()


    print(f"[CONTROLLER] New rows: {len(rows)}", flush=True)


    if not rows:
        return


    events = [
        parse_row(row)
        for row in rows
    ]


    with open(OUTPUT_FILE, "a") as out:

        for event in events:
            out.write(json.dumps(event) + "\n")


    save_offset(rows[-1][0])


    print(
        f"[INGEST] Controller: {len(events)} events",
        flush=True
    )
