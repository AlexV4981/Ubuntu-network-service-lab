# Database and event pipeline

The Flask controller writes operational data to **SQLite**. The ingestion process converts new controller rows and game log lines into JSON-lines event records.

## SQLite schema

Defined by [controller.py](../controller/app/controller.py):

| Table | Key | Purpose |
| --- | --- | --- |
| \`command_history\` | Auto-increment integer \`id\` | Records timestamp, user ID/name, command, result and prior/new container state |
| \`cooldowns\` | Text \`command\` | One expiry timestamp per command, shared across users and configured servers |

The controller uses parameterized SQL statements for [audit inserts](../controller/app/controller.py), [cooldown SELECTs](../controller/app/controller.py) and \`INSERT ... ON CONFLICT ... DO UPDATE\` for the [cooldown UPSERT](../controller/app/controller.py). This demonstrates real SQL persistence but not an atomic transaction across a Docker operation and all log writes.

## Incremental ingestion

- [Controller parser](../ingest/parsers/controller.py): \`SELECT\` with \`WHERE id > ?\`, \`ORDER BY id ASC\`; maps rows to a common event object; appends JSON lines; then records the last processed row ID.
- [Minecraft parser](../ingest/parsers/minecraft.py): reads a configured \`latest.log\` from the previous byte offset and wraps each raw line as an event. It is not a full semantic parser of each gameplay event.
- [Common event structure](../ingest/events.py): fields for source, type, actor, action, result, metadata and timestamp.
- [Example event](../examples/controller-event.json): synthetic identifiers and values only.

## Privacy and reliability

The actual runtime database and exported logs can contain Discord IDs, player names and raw game log text. They belong on the host, **not** in GitHub. The checked-in sample is fabricated.

Event output and checkpoint commits are separate writes: a crash between these steps can replay rows. Log rotation and database replacement also require offset reconciliation. The controller does not record every unsuccessful attempt or cooldown response, so exported events are **not a complete security audit trail**.

The current database is **SQLite, not PostgreSQL or Oracle**. There is no PL/SQL implementation, data-warehouse pipeline, or completed Wazuh integration here.

[Architecture](ARCHITECTURE.md) · [Operations](OPERATIONS.md) · [Security](../SECURITY.md).