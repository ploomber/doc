import json
import sqlite3
import pandas as pd
from enum import Enum
from pathlib import Path
import threading


class TaskStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"


class TaskResultManager:
    def __init__(self, path_to_db):
        self._path_to_db = path_to_db
        self._local = threading.local()
        self._create_db()

    @property
    def connection(self):
        if not hasattr(self._local, "connection"):
            self._local.connection = sqlite3.connect(self._path_to_db)
        return self._local.connection

    def __del__(self):
        if hasattr(self._local, "connection"):
            self._local.connection.close()

    def _create_db(self):
        Path(self._path_to_db).parent.mkdir(parents=True, exist_ok=True)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS task_results (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                result TEXT,
                status TEXT
            )
        """
        )
        self.connection.commit()

    def store_result(self, task_id, result, status):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE task_results
            SET result = ?, status = ?
            WHERE id = ?
        """,
            (json.dumps(result), status.value, task_id),
        )
        self.connection.commit()

    def store_pending_task(self, task_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO task_results (id, user_id, status)
            VALUES (?, ?, ?)
        """,
            (task_id, user_id, TaskStatus.PENDING.value),
        )
        self.connection.commit()

    def get_result(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT result, status FROM task_results WHERE id = ?
        """,
            (task_id,),
        )
        result = cursor.fetchone()
        if result:
            return json.loads(result[0]), result[1]
        return None, None

    def get_user_results(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, result, status FROM task_results WHERE user_id = ?
        """,
            (user_id,),
        )
        results = cursor.fetchall()
        df = pd.DataFrame(results, columns=["task_id", "result", "status"])
        df["result"] = df["result"].apply(safe_load_json)
        return df


def safe_load_json(json_str):
    try:
        return json.loads(json_str)
    except Exception:
        return None
