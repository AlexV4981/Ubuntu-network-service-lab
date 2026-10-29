# Setup and operations

## Prerequisites

- A Linux host with Docker and Docker Compose.
- A Discord bot token, guild ID and control role ID; keep all actual values outside Git.
- Existing target Minecraft containers named \`mc-cobblemon\` and/or \`mc-horror\`, or a reviewed update to [controller configuration](../controller/app/controller.py).
- Log directories for those servers if you want game-log ingestion.

## Environment

From the repository root:

~~~bash
cp .env.example .env
~~~

Fill the placeholders in your **local** \`.env\`. Important variable names:

| Variable | Purpose |
| --- | --- |
| \`DISCORD_TOKEN\` | Private bot authentication token |
| \`DISCORD_GUILD_ID\` | Guild where commands are registered |
| \`MC_CONTROL_ROLE_ID\` | Role permitted to control servers through Discord |
| \`UID\` / \`GID\` | Owner IDs for the bot container |
| \`MC_COBBLEMON_LOG_DIR\` / \`MC_HORROR_LOG_DIR\` | Existing host directories for logs |

The log directories default to relative example locations, not automatically provisioned servers. Never commit a populated \`.env\`.

## Compose lifecycle

~~~bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
docker compose logs -f helpy-bot minecraft-controller ingest
~~~

\`docker compose config --quiet\` validates configuration without printing expanded environment values. For troubleshooting, **do not share** unredacted logs: they may contain usernames, IDs or server data.

## Manual checks

1. Confirm the bot registers \`/ping\`, \`/status\`, \`/up\`, \`/down\` and \`/restart\`.
2. Verify a member **without** the configured role cannot invoke control commands through Discord.
3. Confirm \`/status\` and a permitted control action produce the expected response and SQLite history, without exposing sensitive rows publicly.
4. Confirm the ingestion worker emits controller and Minecraft JSON-lines events from disposable test data.
5. Restart ingestion and inspect offset behavior. Test log rotation and reconnection with a nonproduction server.
6. Confirm the controller HTTP service is **not exposed** to untrusted networks and that only the intended containers can access the Docker socket.

These are **manual verification steps**, not a claim that this documentation change executed the stack or passed tests.

## Important limitations

The Flask controller does not authenticate requests independently; custom HTTP user headers are not proof of identity. Docker socket mounting grants broad host control. A Discord role check is not a substitute for controller authentication or network isolation. See [Security](../SECURITY.md) before deploying beyond a private lab.

[Architecture](ARCHITECTURE.md) · [Data pipeline](DATA_PIPELINE.md).