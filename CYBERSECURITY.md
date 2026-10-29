# Security implementation notes

The current security boundaries and limitations are documented in **[SECURITY.md](SECURITY.md)**. The [topology diagram](docs/ARCHITECTURE.md) maps the Discord bot, Flask controller, Docker socket and ingestion trust boundaries.

The implementation demonstrates [Discord role checks](app/src/main/java/bot/services/PermissionService.java), [control-command enforcement](app/src/main/java/bot/commands/UpCommand.java), [SQLite audit records](controller/app/controller.py), and [incremental event processing](ingest/parsers/controller.py).

**Scope:** Discord-side role checks are implemented; HTTP controller authentication and a complete security monitoring pipeline are **not**. This page remains at its original URL for existing external links.