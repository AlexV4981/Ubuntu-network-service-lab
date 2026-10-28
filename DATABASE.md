# Database Skills and Code

SQLite schema design, parameterized statements, record updates, and incremental event extraction in the Ubuntu service lab.

## Database code at a glance

| What to review | Implementation | What it demonstrates |
| --- | --- | --- |
| Database structure | [Table definitions](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/3a3217b0114083f8a877651aa22680fd2b564d97/controller/app/controller.py#L35-L66) | Two SQLite tables, primary keys, NOT NULL constraints, and an automatically assigned history ID |
| Writing structured records | [Audit INSERT](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/3a3217b0114083f8a877651aa22680fd2b564d97/controller/app/controller.py#L67-L115) | Parameterized INSERT with seven bound values, a timestamp, and an explicit commit |
| Looking up existing records | [Cooldown SELECT](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/3a3217b0114083f8a877651aa22680fd2b564d97/controller/app/controller.py#L220-L262) | Parameterized SELECT with a WHERE condition, then a cooldown decision based on the stored expiry |
| Updating existing records | [Cooldown UPSERT](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/3a3217b0114083f8a877651aa22680fd2b564d97/controller/app/controller.py#L263-L296) | INSERT ... ON CONFLICT ... DO UPDATE to insert a command cooldown or update its existing expiry |
| Extracting new records | [Incremental SELECT and export](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/3a3217b0114083f8a877651aa22680fd2b564d97/ingest/parsers/controller.py#L62-L134) | Parameterized WHERE id > ?, explicit column selection, and ORDER BY id ASC |
| Preparing data for analysis | [Row-to-event mapping](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/3a3217b0114083f8a877651aa22680fd2b564d97/ingest/parsers/controller.py#L29-L61) | Mapping database fields into a consistent event format, writing JSON lines, and saving a processing checkpoint |

**Suggested review order:** table definitions → audit INSERT → cooldown UPSERT → incremental extraction. No running Discord account or game server is needed to read the database implementation.

## Database design

| Table | Key and constraints | Stored data and purpose |
| --- | --- | --- |
| `command_history` | `id INTEGER PRIMARY KEY AUTOINCREMENT`; all other fields are NOT NULL | Timestamp, user ID/name, command, result, prior state, and new state provide a record of handled activity |
| `cooldowns` | `command TEXT PRIMARY KEY`; `expires INTEGER NOT NULL` | One expiry per command, persisted between controller restarts |

These tables serve separate purposes and have no foreign-key relationship. Cooldowns are shared across users and configured servers for each command.

### Record writes and updates

The controller binds values separately from SQL text using SQLite's `?` placeholders. [Audit INSERT](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/3a3217b0114083f8a877651aa22680fd2b564d97/controller/app/controller.py#L67-L115) stores a command-history record; [Cooldown UPSERT](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/3a3217b0114083f8a877651aa22680fd2b564d97/controller/app/controller.py#L263-L296) handles the existing-record case with:

```sql
INSERT INTO cooldowns(command, expires)
VALUES (?, ?)
ON CONFLICT(command)
DO UPDATE SET expires=excluded.expires
```

The write functions call `conn.commit()` to persist their changes. The current implementation does not include an explicit rollback workflow or an atomic transaction spanning the Docker action, cooldown update, and audit write.

### From database rows to structured events

The [Incremental SELECT and export](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/3a3217b0114083f8a877651aa22680fd2b564d97/ingest/parsers/controller.py#L62-L134) reads records above the last saved ID in ascending order. It maps each row into an event containing `timestamp`, `source`, `event_type`, `actor`, `action`, `result`, and `metadata`, appends events to a JSON-lines file, then saves the final processed ID.

[View a synthetic controller event](examples/controller-event.json) · [View the common event builder](ingest/events.py)

The example contains fabricated identifiers. Runtime databases, actual log exports, and checkpoints are excluded from the current source tree.

## Scope and current limits

This project demonstrates **SQL/SQLite database structures, record insertion and updates, audit data, and incremental extraction**. Oracle/PLSQL and production data-correction scripts are not implemented.

The API records several successful and blocked actions, but not every failure or cooldown rejection. Export and checkpoint writes are separate operations, so crash recovery can replay records; replacing a database also requires checkpoint handling. More operational limitations and the setup instructions are below.


[Cybersecurity skills and code](CYBERSECURITY.md) · [Project overview and setup](README.md)
