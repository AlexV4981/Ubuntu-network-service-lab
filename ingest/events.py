from datetime import datetime


def create_event(
    source,
    event_type,
    actor=None,
    action=None,
    result=None,
    metadata=None,
    timestamp=None
):
    return {
        "timestamp": timestamp or datetime.now().isoformat(),

        "source": source,
        "event_type": event_type,

        "actor": actor or {
            "id": None,
            "name": None
        },

        "action": action or {
            "name": "unknown",
            "category": "unknown"
        },

        "result": result or {
            "status": "unknown"
        },

        "metadata": metadata or {}
    }
