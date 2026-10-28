# Ubuntu Network Service Lab

A personal Ubuntu lab for managing Minecraft containers through a Java Discord bot and Python Flask API. SQLite stores command history and cooldowns; a Python ingestion service converts controller records and Minecraft logs into structured events.

## Implemented features

- Discord commands for status, start, stop, restart, and bot health.
- Discord role checks for start, stop, and restart commands.
- Controller checks for service state, persistent control-command cooldowns, and an in-memory status request limit.
- SQLite tables with primary keys and NOT NULL constraints, parameterized queries, and ON CONFLICT updates for cooldown records.
- Command-history records containing the user, command, result, timestamp, and before/after state.
- Incremental ingestion using SQLite record IDs and per-server log offsets.
- Newline-delimited JSON event output for later analysis or SIEM integration.

## Architecture

```mermaid
flowchart TD
    A[Discord bot Java JDA] --> B[Flask controller]
    B --> C[Docker Engine and Minecraft containers]
    B --> D[SQLite command history and cooldowns]
    D --> E[Python ingestion]
    C -->|Read only log mounts| E
    E --> F[Structured event files]
```

## Requirements

- A Linux Docker host with Docker Compose and access to `/var/run/docker.sock`.
- A Discord bot token, guild ID, and role ID for permitted operators. Invite the bot to that guild with bot and application-command scopes and permissions appropriate to its commands.
- Existing Minecraft containers named `mc-cobblemon` and/or `mc-horror`, with readable log directories. This repository does not provision those game servers.

The controller selects the most recently started running configured server. When none is running, `/up` attempts to start `mc-horror`. Change `SERVERS` and `DEFAULT_SERVER` in `controller/app/controller.py` to match a different setup.

## Setup

```bash
git clone https://github.com/AlexV4981/Ubuntu-network-service-lab.git
cd Ubuntu-network-service-lab
cp .env.example .env
```

Edit `.env` before starting:

| Variable | Purpose |
| --- | --- |
| `DISCORD_TOKEN` | Private bot token; never commit it |
| `DISCORD_GUILD_ID` | Guild where commands are registered |
| `MC_CONTROL_ROLE_ID` | Discord role allowed to run control commands |
| `UID` and `GID` | Linux user/group IDs for the bot container; obtain with `id -u` and `id -g` |
| `MC_COBBLEMON_LOG_DIR` | Host directory containing the Cobblemon server's `latest.log` |
| `MC_HORROR_LOG_DIR` | Host directory containing the Horror server's `latest.log` |

Set the log variables to your existing directories, preferably absolute paths. Defaults point to local example directories under `minecraft/`; they do not create or configure game servers. Existing installations using the old hardcoded host paths must set these variables before recreating containers.

```bash
docker compose config --quiet
docker compose up -d --build
docker compose logs -f helpy-bot minecraft-controller ingest
```

`docker compose config --quiet` validates configuration without printing the resolved bot token. The Java bot is built in a Maven Docker build stage; committed JARs and `target/` files are unnecessary.

## Commands

| Command | Behavior |
| --- | --- |
| `/ping` | Bot response check |
| `/status` | Active server status; controller limits requests |
| `/up` | Start the default server if no configured server is running |
| `/down` | Stop the active server |
| `/restart` | Restart the active server |

Control commands use a 180-second cooldown per command, shared across users and configured servers. The status limit is three requests per 60 seconds across the controller process.

## Data and ingestion

- `controller/data/controller.db`: runtime SQLite database with `command_history` and `cooldowns` tables.
- `ingest/processed/controller.json`: newline-delimited controller events selected by increasing database ID.
- `ingest/processed/minecraft.json`: newline-delimited Minecraft events containing source log lines.
- `ingest/state/`: local ingestion checkpoints, created at runtime.

Despite the `.json` suffix, each output line is an independent JSON object. The ingestion service polls every five seconds. Minecraft events currently wrap raw log lines rather than extracting detailed gameplay fields. Controller events map database fields to a common event structure.

Generated output, offsets, databases, and build files are ignored by Git. Keep runtime logs private: they can contain user identifiers, chat, addresses, and other operational details. A synthetic output example is available in `examples/controller-event.json`.

## Validation

1. Confirm the bot connects and `/ping` responds.
2. Confirm a user without the configured role cannot run control commands.
3. Use `/status` and a permitted control command; inspect the resulting `command_history` rows.
4. Confirm the ingestion output contains normalized controller events and Minecraft log events.
5. Restart ingestion and verify existing checkpoints prevent normal replay of previously processed records.

These are manual checks, not an automated test suite. A running Discord bot and Docker/Minecraft environment are needed for end-to-end validation.

## Current limitations

- This is a trusted-host lab. The controller mounts the host Docker socket, which grants powerful access to the Docker host. Do not expose the controller to untrusted networks.
- Discord role checks are enforced by the bot. The controller has no API authentication and trusts incoming user headers; another client with network access can bypass the bot's checks.
- Services share one Compose network; separate security tiers are planned, not implemented.
- The API records several successful and blocked actions, but not every failure or cooldown rejection. Audit records are not a complete security audit trail.
- Status limiting is process-local. State checks and cooldown operations are not atomic across concurrent requests.
- Controller ingestion assumes monotonically increasing database IDs. Checkpoints require care if the database is replaced. File-output writes and checkpoint updates are not one transaction, so crash recovery may replay events.
- Minecraft log rotation handling detects a saved offset larger than the current file, but is not a complete rotation/replacement strategy.
- Wazuh integration and alert rules are not implemented.

## Planned improvements

- Wazuh ingestion, alert rules, and dashboards.
- Controller authentication and narrower Docker permissions.
- Network segmentation and additional container hardening.
- More complete failure logging, ingestion recovery, and automated tests.
