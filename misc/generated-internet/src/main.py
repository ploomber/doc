from src.server import create_server
from src.settings import Settings

app = create_server(Settings())
