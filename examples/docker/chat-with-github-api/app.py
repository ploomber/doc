from fastapi import FastAPI, HTTPException
from typing import Dict 
from typing import Any
from pydantic import BaseModel
import task
import os

from llama_index.core import VectorStoreIndex
from llama_index.readers.github import GithubClient, GithubRepositoryReader

from database import db_session
from models import RepoModel

app = FastAPI() # <- the ASGI entrypoint

class Repo(BaseModel):
    owner: str
    name: str
    branch: str

class Question(BaseModel):
    repo_id: str
    question: str

@app.get('/')
def index() -> Dict:
    return {'hello': 'world'}


@app.post('/scrape')
def scrape(repo: Repo) -> dict[str, Any]: # maybe change repo from str
    # Enter into DB
    id = f"{repo.owner}-{repo.name}-{repo.branch}"
    status = "pending"
    path = f"/indexes/{repo.owner}/index_{repo.name}_{repo.branch}.pickle"
    repoModel = RepoModel(id=id, status=status, path=path)
    db_session.add(repoModel)

    # If repo has already been entered, exception
    try:
        db_session.commit()
    except Exception as e:
        print(e)
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Repo already exists") from e

    print(f"Repos: {RepoModel.show_all()}")

    task.download_repo.delay(id=id, owner=repo.owner, name=repo.name, branch=repo.branch, path=path)
    
    return {'id': id, 'status': status, 'path': path}


@app.get('/status/{repo_id}')
def status(repo_id) -> dict[str, Any]:
    try:
        stat = RepoModel.get_repo_status(repo_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Repo not found") from e
    
    return {'id': repo_id, 'status': stat}


@app.post('/ask')
def ask(question: Question) -> dict[str, Any]: # maybe change repo from str
    return {'question': question, 'answer': 'some answer'}


@app.get('/clear')
def clear(exception=None):
    deleted = RepoModel.query.delete()
    return {'deleted': deleted}
