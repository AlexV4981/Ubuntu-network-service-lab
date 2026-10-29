# Security and data-handling limitations

This is a **homelab** for learning service orchestration, access checks and event ingestion. It is not a production-ready security or hosting system.

## Primary risk: unauthenticated Docker controller

The Java bot checks a Discord role before issuing selected control commands, but the Python Flask controller's HTTP API does **not** independently verify caller credentials. The user identity fields in HTTP request headers are caller-supplied metadata, not authenticated identities. The controller mounts the Docker Engine socket, granting high-impact host management capabilities to anyone who can successfully compromise or reach its control API.

**Do not publish or port-forward the controller.** Restrict its network reachability to explicitly trusted local components. A stronger future design should authenticate and authorize controller requests, minimize Docker privileges, and apply network isolation with corresponding tests.

## Data privacy

- Keep \`.env\`, Discord tokens, real user/guild/role identifiers, private host paths and credentials out of public commits.
- Keep \`controller/data\`, \`ingest/processed\`, \`ingest/state\`, game logs, backups, crash dumps and screenshots containing private identifiers out of source control.
- Game-log ingestion can preserve **raw lines** containing player identities and chat. Audit output is not suitable for public posting without review and redaction.
- [examples/controller-event.json](examples/controller-event.json) uses synthetic records; it is not a sample of real user activity.

The repository includes a [safe environment template](.env.example) and ignore rules. Ignoring a file does not erase it if it was already committed. Any previously exposed credential must be rotated; historical cleanup is a separate reviewed operation.

## Security claims and scope

- Role checks at the Discord layer and parameterized SQL are demonstrable in code.
- The application lacks controller-level API authentication and a complete audit of all failed actions.
- The ingestion pipeline is an event formatter, **not** an active SIEM or intrusion-detection deployment.
- Docker Compose configuration demonstrates orchestration, but the application is **not independently penetration-tested**.

Report possible vulnerabilities privately if GitHub private vulnerability reporting is enabled; do not post credentials or exploitable host details in public issues.

[Architecture](docs/ARCHITECTURE.md) · [Operations](docs/OPERATIONS.md) · [Database pipeline](docs/DATA_PIPELINE.md).