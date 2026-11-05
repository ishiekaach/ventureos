from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "ventureos.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
