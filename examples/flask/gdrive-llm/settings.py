from pathlib import Path
from dotenv import load_dotenv
from os import environ

_path_to_here = Path(__file__).parent.resolve()
path_to_env = Path(_path_to_here / ".env")

DB_URI = f"sqlite:///{_path_to_here}/gdrive_loader.db"


if path_to_env.exists():
    load_dotenv(path_to_env)


OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
GOOGLE_CREDENTIALS_BASE64 = environ.get("GOOGLE_CREDENTIALS_BASE64")
