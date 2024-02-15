from pathlib import Path
import sqlite3
import json
import logging

from aiutils import CACHE_PATH
from aiutils.frozenjson import FrozenJSON

logger = logging.getLogger(__name__)


def qualified_name(obj):
    return obj.__module__ + "." + obj.__qualname__


class APICache:
    def __init__(self, api_function, path_to_db=None) -> None:
        self._path_to_db = path_to_db or CACHE_PATH
        self._connection = None
        self._api_function = api_function
        self._qualified_name = qualified_name(api_function)

        if not Path(self._path_to_db).exists():
            self.create_db()

    @property
    def connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self._path_to_db)

        return self._connection

    def __del__(self):
        if self._connection is not None:
            self._connection.close()

    def create_db(self):
        Path(self._path_to_db).parent.mkdir(parents=True, exist_ok=True)
        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS api_calls (
                qualified_name TEXT,
                kwargs TEXT,
                response TEXT
            )
        """
        )

        self.connection.commit()

    def insert(self, *, kwargs: dict, response: dict):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO api_calls (qualified_name, kwargs, response)
            VALUES (?, ?, ?)
        """,
            (
                self._qualified_name,
                json.dumps(kwargs),
                json.dumps(response),
            ),
        )

        self.connection.commit()

    def lookup(self, *, kwargs: dict):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT response FROM api_calls
            WHERE qualified_name = ? AND kwargs = ?
        """,
            (self._qualified_name, json.dumps(kwargs)),
        )

        response = cursor.fetchone()

        return None if response is None else json.loads(response[0])

    def __call__(self, **kwargs):
        response = self.lookup(kwargs=kwargs)

        if response is None:
            logger.info("Cache miss, calling API.")
            response = self._api_function(**kwargs).model_dump()
            self.insert(
                kwargs=kwargs,
                response=response,
            )
        else:
            logger.info("Cache hit, using cached response.")

        # return FrozenJSON(response) to enable attribute access
        return FrozenJSON(response)
