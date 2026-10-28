from pathlib import Path

# Location of the ingest folder
INGEST_DIR = Path(__file__).resolve().parent

# Subdirectories
PROCESSED_DIR = INGEST_DIR / "processed"
STATE_DIR = INGEST_DIR / "state"
RAW_DIR = INGEST_DIR / "raw"

# Make sure folders exist
PROCESSED_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)
RAW_DIR.mkdir(exist_ok=True)
