# Ubuntu Network Service Lab

A self-hosted service-control and event-ingestion lab combining a **Java Discord bot (JDA)**, a **Python Flask controller**, **Docker Compose**, and **SQLite**. It explores service administration, permission checks, cooldowns, audit records, and structured log processing on Linux.

[System topology](docs/ARCHITECTURE.md) · [Setup and operations](docs/OPERATIONS.md) · [Database and events](docs/DATA_PIPELINE.md) · [Security boundaries](SECURITY.md)

## How it works

A Discord slash command reaches the Java bot. Control commands are checked against a configured Discord role before the bot calls the Flask controller over an internal Compose network. The controller selects/configures a Minecraft container, performs start/stop/status operations through the Docker API, and records some actions in SQLite. A separate ingestion service polls those SQLite records and read-only game logs and produces JSON-lines event files.

The [topology diagram](docs/ARCHITECTURE.md) shows these components, storage mounts, and trust boundaries.

## Implementation

| Area | Source | What it demonstrates |
| --- | --- | --- |
| Java command dispatch | [SlashCommandListener](app/src/main/java/bot/listeners/SlashCommandListener.java) · [MinecraftService](app/src/main/java/bot/services/MinecraftService.java) | JDA commands and HTTP service adapter |
| Access check | [PermissionService](app/src/main/java/bot/services/PermissionService.java) · [UpCommand](app/src/main/java/bot/commands/UpCommand.java) | Discord-role check before submitting a control request |
| Controller | [Flask application](controller/app/controller.py) | Docker container state operations, cooldown logic, HTTP endpoints |
| SQLite | [Schema and audit code](controller/app/controller.py) | \`command_history\`, \`cooldowns\`, bound SQL parameters and an UPSERT |
| Event ingestion | [Controller parser](ingest/parsers/controller.py) · [Game log parser](ingest/parsers/minecraft.py) | Incremental records, byte offsets, JSON-lines export |
| Runtime | [Compose](docker-compose.yml) · [Environment template](.env.example) | Java bot, controller and ingestion containers |

The [database walkthrough](docs/DATA_PIPELINE.md) links directly to the schema, audit writes and extraction code.

## Layout

~~~text
app/                    Java 21 Discord bot and permission checks
controller/             Flask control API and SQLite persistence
ingest/                 Controller/game-log event readers and exporters
examples/               Synthetic sample events (not real user data)
docs/
  ARCHITECTURE.md       Data flow, topology and trust boundaries
  DATA_PIPELINE.md      SQL schema, writes and ingestion behavior
  OPERATIONS.md         Setup and manual validation
SECURITY.md             Known exposure risks and privacy expectations
docker-compose.yml      Service orchestration
.env.example            Placeholder environment variables
~~~

## Quick start

Requires a Docker-enabled Linux host, a Discord bot and guild, and separately provisioned Minecraft containers. This repository **does not** provision Minecraft servers.

~~~bash
cp .env.example .env
# Replace placeholders locally; never commit your real .env
docker compose config --quiet
docker compose up -d --build
~~~

Before running, review [Operations](docs/OPERATIONS.md) and [Security](SECURITY.md), especially the Docker socket and controller API trust boundary. This is a **trusted-network lab**, not a production-hardened public management service.

## Data handling and limitations

The controller records command history and cooldowns in a runtime SQLite database. The ingestion service appends structured JSON-lines exports; raw game log lines can contain player identities or chat and must remain private. Only [synthetic examples](examples/controller-event.json) belong in the public repository.

The controller does **not** authenticate HTTP requests independently; Discord-role enforcement protects the bot command path, not arbitrary clients that can reach the controller. The Docker socket grants the controller powerful host capabilities. No Wazuh integration or security certification is claimed. See [Security](SECURITY.md) for limitations and mitigation priorities.

Related: [Debian Network Service Lab](https://github.com/AlexV4981/debian-network-service-lab) explores Python TCP wake-on-demand and idle shutdown.