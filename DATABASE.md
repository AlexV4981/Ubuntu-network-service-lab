# Database implementation notes

The canonical database walkthrough is **[docs/DATA_PIPELINE.md](docs/DATA_PIPELINE.md)**.

Direct code references: [SQLite schema and parameterized writes](controller/app/controller.py) · [Incremental controller query](ingest/parsers/controller.py) · [Common event format](ingest/events.py) · [Synthetic event](examples/controller-event.json).

The implementation uses SQLite with command history, cooldown updates and incremental JSON-lines export. This page stays at its original URL for existing external links.