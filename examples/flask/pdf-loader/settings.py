from pathlib import Path
from dotenv import load_dotenv
from os import environ

_path_to_here = Path(__file__).parent.resolve()
path_to_env = Path(_path_to_here / ".env")

DB_URI = f"sqlite:///{_path_to_here}/pdf_loader.db"


if path_to_env.exists():
    load_dotenv(path_to_env)


OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
PATH_TO_UPLOADS = Path(_path_to_here / "uploads")

if not PATH_TO_UPLOADS.exists():
    PATH_TO_UPLOADS.mkdir(parents=True, exist_ok=True)
