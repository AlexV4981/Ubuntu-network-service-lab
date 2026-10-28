from flask import Flask, jsonify, request
import docker
import sqlite3
import time
from datetime import datetime


app = Flask(__name__)

client = docker.from_env()


SERVERS = {
    "mc-cobblemon": "cobblemon",
    "mc-horror": "horror"
}

DEFAULT_SERVER = "mc-horror"

DATABASE = "/data/controller.db"

COMMAND_COOLDOWN = 180  # 3 minutes

STATUS_LIMIT = 3
STATUS_WINDOW = 60


status_queries = []


# =========================
# Database
# =========================

def init_db():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cooldowns (
        command TEXT PRIMARY KEY,
        expires INTEGER NOT NULL
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS command_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT NOT NULL,
        user_id TEXT NOT NULL,
        user TEXT NOT NULL,
        command TEXT NOT NULL,
        result TEXT NOT NULL,
        prior_state TEXT NOT NULL,
        new_state TEXT NOT NULL
    )
    """)


    conn.commit()
    conn.close()



def log_command(
        user_id,
        user,
        command,
        result,
        prior_state,
        new_state
):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()


    cursor.execute("""
    INSERT INTO command_history
    (
        time,
        user_id,
        user,
        command,
        result,
        prior_state,
        new_state
    )

    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        datetime.now().isoformat(),
        user_id,
        user,
        command,
        result,
        prior_state,
        new_state
    ))


    conn.commit()
    conn.close()



# =========================
# Docker
# =========================


def get_container(container_name):

    try:

        container = client.containers.get(
            container_name
        )

        container.reload()

        return container


    except docker.errors.NotFound:

        return None



def get_active_container():

    active = None
    newest_time = None


    for container_name in SERVERS:

        container = get_container(container_name)


        if container is None:
            continue


        if container.status != "running":
            continue


        started = container.attrs["State"]["StartedAt"]


        if newest_time is None or started > newest_time:

            newest_time = started
            active = container


    return active


def get_server_state(container):

    if container is None:
        return "offline"


    if container.status != "running":

        return "offline"


    health = None


    try:

        health = container.attrs["State"]["Health"]["Status"]

    except KeyError:

        pass



    if health == "starting":

        return "starting"


    if health == "healthy":

        return "online"


    return "online"



def get_server_name(container):

    if container is None:

        return "none"


    return SERVERS.get(
        container.name,
        "unknown"
    )

# =========================
# Cooldowns
# =========================

def check_command_cooldown(command):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()


    cursor.execute(
        "SELECT expires FROM cooldowns WHERE command=?",
        (command,)
    )


    result = cursor.fetchone()

    conn.close()


    if not result:

        return True, None



    remaining = result[0] - int(time.time())


    if remaining > 0:

        minutes = remaining // 60
        seconds = remaining % 60


        return False, (
            f"Cooldown active. "
            f"Try again in {minutes}m {seconds}s"
        )


    return True, None



def activate_cooldown(command):

    expires = int(time.time()) + COMMAND_COOLDOWN


    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()


    cursor.execute("""
    INSERT INTO cooldowns(command, expires)

    VALUES (?, ?)

    ON CONFLICT(command)

    DO UPDATE SET expires=excluded.expires
    """,
    (
        command,
        expires
    ))


    conn.commit()
    conn.close()



# =========================
# Status Limit
# =========================

def check_status_limit():

    global status_queries


    now = time.time()


    status_queries = [
        x for x in status_queries
        if now - x < STATUS_WINDOW
    ]


    if len(status_queries) >= STATUS_LIMIT:

        return False



    status_queries.append(now)

    return True



# =========================
# Routes
# =========================

@app.get("/health")
def health():

    return "controller is online"


@app.get("/active-server")
def active_server():

    container = get_active_container()


    if container is None:

        return {
            "container": None,
            "server": None
        }


    return {
        "container": container.name,
        "server": SERVERS[container.name]
    }


@app.get("/status")
def status():

    user_id = request.headers.get(
        "X-User-ID",
        "Unknown"
    )

    user = request.headers.get(
        "X-User",
        "Unknown"
    )


    if not check_status_limit():

        log_command(
            user_id,
            user,
            "status",
            "rate_limited",
            "unknown",
            "unknown"
        )

        return "Status limit reached. Try again later."



    container = get_active_container()

    state = get_server_state(container)

    server_name = get_server_name(container)


    log_command(
        user_id,
        user,
        "status",
        "success",
        state,
        state
    )


    return f"{server_name} server is {state}"





@app.post("/up")
def up():

    user_id = request.headers.get(
        "X-User-ID",
        "Unknown"
    )

    user = request.headers.get(
        "X-User",
        "Unknown"
    )

    container = get_active_container()

    state = get_server_state(container)

    if container is None:
        container = client.containers.get(DEFAULT_SERVER)

    state = get_server_state(container)


    if state == "online":

        log_command(
            user_id,
            user,
            "up",
            "blocked",
            state,
            state
        )


        return "Server already active"



    if state in ["starting", "stopping"]:

        log_command(
            user_id,
            user,
            "up",
            "blocked",
            state,
            state
        )


        return f"Server unavailable: {state}"



    allowed, message = check_command_cooldown("up")


    if not allowed:

        return message



    container.start()


    activate_cooldown("up")


    log_command(
        user_id,
        user,
        "up",
        "success",
        "offline",
        "starting"
    )


    return "Starting server"



@app.post("/down")
def down():

    user_id = request.headers.get(
        "X-User-ID",
        "Unknown"
    )

    user = request.headers.get(
        "X-User",
        "Unknown"
    )


    container = get_active_container()

    state = get_server_state(container)



    if state == "offline":

        log_command(
            user_id,
            user,
            "down",
            "blocked",
            state,
            state
        )


        return "Server already offline"



    if state in ["starting", "stopping"]:

        log_command(
            user_id,
            user,
            "down",
            "blocked",
            state,
            state
        )


        return f"Server unavailable: {state}"



    allowed, message = check_command_cooldown("down")


    if not allowed:

        return message



    container.stop()


    activate_cooldown("down")


    log_command(
        user_id,
        user,
        "down",
        "success",
        "online",
        "stopping"
    )


    return "Shutting down server"



@app.post("/restart")
def restart():

    user_id = request.headers.get(
        "X-User-ID",
        "Unknown"
    )

    user = request.headers.get(
        "X-User",
        "Unknown"
    )


    container = get_active_container()

    state = get_server_state(container)



    if state != "online":

        log_command(
            user_id,
            user,
            "restart",
            "blocked",
            state,
            state
        )


        return f"Server unavailable: {state}"



    allowed, message = check_command_cooldown("restart")


    if not allowed:

        return message



    container.restart()


    activate_cooldown("restart")


    log_command(
        user_id,
        user,
        "restart",
        "success",
        "online",
        "starting"
    )


    return "Restarting server"



# Create database on startup

init_db()


app.run(
    host="0.0.0.0",
    port=5000
)

