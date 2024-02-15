from pathlib import Path

__version__ = "0.1dev"

CACHE_PATH = Path("~/.aiutils/cache.db").expanduser()
CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
