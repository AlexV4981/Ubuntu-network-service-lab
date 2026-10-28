# Recruiter Quick Tour

**Two-minute overview: Python, Java, Linux, access controls, audit logging, and structured data.**

This personal lab manages Minecraft containers through a Java Discord bot and Python Flask API. It provides concrete examples of how I connect application logic, operational controls, and records that can be reviewed when troubleshooting.

## Start with these three examples

| Review | Click to see the evidence | What to look for |
| --- | --- | --- |
| **1. Role-based command access** | [Role membership check](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/a0df3379fabcc0e47a75e7ec0f598479b3d644f4/app/src/main/java/bot/services/PermissionService.java) · [Enforcement before a start command](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/a0df3379fabcc0e47a75e7ec0f598479b3d644f4/app/src/main/java/bot/commands/UpCommand.java) | The bot checks the configured Discord role and rejects an unauthorized control request before calling the controller |
| **2. Validation and audit records** | [Python controller](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/a0df3379fabcc0e47a75e7ec0f598479b3d644f4/controller/app/controller.py) | `init_db` defines the SQLite tables; `log_command` binds audit values; `check_command_cooldown` and `activate_cooldown` read and update cooldown records; routes check service state |
| **3. Structured event ingestion** | [Database extraction and mapping](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/a0df3379fabcc0e47a75e7ec0f598479b3d644f4/ingest/parsers/controller.py) · [Common event structure](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/a0df3379fabcc0e47a75e7ec0f598479b3d644f4/ingest/events.py) · [Synthetic output example](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/a0df3379fabcc0e47a75e7ec0f598479b3d644f4/examples/controller-event.json) | A parameterized ID-based query selects new rows, maps them to events, and saves a processing checkpoint |

## Skills demonstrated

- **Python and Java:** Flask controller, JDA bot, and Python ingestion.
- **Security fundamentals:** bot-layer role permissions, validation, command cooldowns, and activity records.
- **SQL:** table definitions, primary keys, NOT NULL constraints, parameterized queries, and conflict-handling updates.
- **Linux and containers:** [Docker Compose configuration](https://github.com/AlexV4981/Ubuntu-network-service-lab/blob/a0df3379fabcc0e47a75e7ec0f598479b3d644f4/docker-compose.yml) connecting the bot, controller, and ingestion service.

## Scope

The role checks protect the Discord commands; the controller does not yet authenticate API callers. Some outcomes are logged, but the records are not a complete security audit trail. Wazuh integration and network segmentation remain planned. This is a lab project, with no claim of production security operations or penetration-testing experience.

[Read the database walkthrough and setup instructions](README.md) · [View the separate Debian Linux lab](https://github.com/AlexV4981/debian-network-service-lab/blob/main/START_HERE.md)
