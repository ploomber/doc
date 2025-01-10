from sqlalchemy import create_engine, event
from gdrive_loader import SETTINGS
from gdrive_loader.models import Base
import sqlite_vec  # Import your SQLite extension module

engine = create_engine(SETTINGS.DB_URI)


@event.listens_for(engine, "connect")
def load_sqlite_extension(dbapi_connection, connection_record):
    # Enable extension loading
    dbapi_connection.enable_load_extension(True)

    # Load the SQLite vector extension
    sqlite_vec.load(dbapi_connection)

    # Disable extension loading for security
    dbapi_connection.enable_load_extension(False)


if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(engine)
