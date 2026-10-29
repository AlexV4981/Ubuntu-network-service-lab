# System architecture and topology

The lab has three application services (Java bot, Flask controller, Python ingestion) and **existing external Minecraft containers**. Only the bot, controller and ingestion service are provisioned by this repository.

## Container and data topology

~~~mermaid
flowchart TD
    USER["Discord user"]
    DISC["Discord service"]
    subgraph HOST["Linux Docker host"]
      subgraph NET["helpy-network: Compose network"]
        BOT["Java JDA bot"]
        API["Python Flask controller"]
        ING["Python ingestion worker"]
      end
      SOCK["Docker Engine API socket"]
      MC["Existing Minecraft containers"]
      SQL[("SQLite: controller/data/controller.db")]
      RAW["Read-only game log mounts"]
      OUT[("ingest/processed/*.json + checkpoints")]
    end
    USER --> DISC
    DISC -->|"Slash commands"| BOT
    BOT -->|"Role check for control commands"| BOT
    BOT -->|"HTTP status / control"| API
    API -->|"Container lifecycle calls"| SOCK
    SOCK --> MC
    API -->|"Command history and cooldowns"| SQL
    SQL -->|"Read-only mount, ID-based polling"| ING
    MC --> RAW
    RAW -->|"Read-only mount"| ING
    ING -->|"Append events and offsets"| OUT
~~~

## Components

1. The [Java command listener](../app/src/main/java/bot/listeners/SlashCommandListener.java) dispatches slash commands. The [role checker](../app/src/main/java/bot/services/PermissionService.java) is used by the control command handlers, such as [UpCommand](../app/src/main/java/bot/commands/UpCommand.java).
2. [MinecraftService](../app/src/main/java/bot/services/MinecraftService.java) makes HTTP calls to the Flask controller over the Compose network and supplies user labels as HTTP headers.
3. The [Flask controller](../controller/app/controller.py) has no independent API authentication; it accesses Docker through the mounted host socket and maintains SQLite \`command_history\` and \`cooldowns\` records.
4. [ingest/ingest.py](../ingest/ingest.py) polls every five seconds. [Controller ingestion](../ingest/parsers/controller.py) selects rows after the last recorded ID. [Minecraft log ingestion](../ingest/parsers/minecraft.py) reads lines after a byte offset and preserves the raw line in event metadata.
5. Structured events are written as **JSON Lines** (one JSON object per line), despite the \`.json\` suffix. [Synthetic event example](../examples/controller-event.json).

## Trust boundaries

| Boundary | Exposure and implication |
| --- | --- |
| Discord user → bot | Role checks protect selected bot control commands; this is **not** API-level authentication. |
| Bot/network peer → Flask | Any caller with controller network access can reach its control endpoints. Treat the Compose network as trusted, not publicly routable. |
| Controller → Docker socket | A compromised controller can act through Docker Engine with powerful host-equivalent permissions. |
| Controller → SQLite | Records include user identifiers and command metadata; the runtime database should remain private. |
| Minecraft logs → ingestion | Read-only mounts avoid write access to server logs, but content may include real identities, chat or network details. |
| Ingestion → event files | Exports and checkpoints are runtime data, not source-control artifacts or necessarily complete audit trails. |

This is a **development/homelab topology**, not a claim of a hardened production service. See [Security](../SECURITY.md) and [Operations](OPERATIONS.md).