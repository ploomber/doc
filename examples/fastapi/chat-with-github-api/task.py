# in file task.py
from celery.app import Celery
import os
import time
from pathlib import Path
import pickle

from llama_index.core import VectorStoreIndex
from llama_index.readers.github import GithubClient, GithubRepositoryReader

from database import db_session
from models import RepoModel

INDEXES = Path("indexes")

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

app = Celery(__name__, broker=redis_url, backend=redis_url)


@app.task
def dummy_task(repo_name):
    time.sleep(5)
    print(f"Done! {repo_name}")


@app.task
def download_repo(id, owner, name, branch, path):
    RepoModel.update_repo_status(id, "pending")
    db_session.commit()

    try:
        gh_token = os.getenv("GITHUB_TOKEN")
        client = GithubClient(gh_token)
        loader = GithubRepositoryReader(
                github_client=client,
                owner=owner,
                repo=name,
                use_parser=False,
                verbose=True,
                timeout=None,
                retries=2,
                concurrent_requests=2,
                # ignore_directories=None,
                # ignore_file_extensions=None
            )
        docs = loader.load_data(branch=branch)
        index = VectorStoreIndex.from_documents(docs)
    except Exception:
        RepoModel.update_repo_status(id, "failed")
        db_session.commit()
        raise

    if not INDEXES.exists():
        Path.mkdir("indexes", exist_ok=True)

    full_path = INDEXES / path
    full_path.touch()

    with full_path.open("wb") as f:
        pickle.dump(index, f, pickle.HIGHEST_PROTOCOL)

    RepoModel.update_repo_status(id, "finished")
    db_session.commit()
