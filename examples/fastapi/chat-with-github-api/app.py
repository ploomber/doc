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

from pathlib import Path
import pickle

app = FastAPI() # <- the ASGI entrypoint

INDEXES = Path("indexes")

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
    status = None
    path = None

    # Check if repo has been entered
    try:
        status = RepoModel.get_repo_status(id)
    except:
        pass

    if status == "pending":
        raise HTTPException(status_code=500, detail="Repo is being parsed.")
    elif status == "finished":
         raise HTTPException(status_code=500, detail="Repo already parsed successfully.")
    elif status == "failed":
        path = RepoModel.get_repo_path(id)
        status = "pending"
    else: # status == None
        path = f"{repo.owner}_{repo.name}_{repo.branch}.pickle"
        status = "pending"
        repoModel = RepoModel(id=id, status=status, path=path)
        db_session.add(repoModel)
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise HTTPException(status_code=500, detail="Repo already exists.") from e

    # Show current repos
    show()

    # Send download task to celery
    task.download_repo.delay(id=id, owner=repo.owner, name=repo.name, branch=repo.branch, path=path)
    
    return {'id': id, 'status': status, 'path': path}


@app.get('/status/{repo_id}')
def status(repo_id) -> dict[str, Any]:
    try:
        stat = RepoModel.get_repo_status(repo_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Repo not found.") from e
    
    return {'id': repo_id, 'status': stat}


@app.post('/ask')
def ask(question: Question) -> dict[str, Any]: # maybe change repo from str
    answer = answer_question(question.repo_id, question.question)
    return {'question': question, 'answer': answer}


@app.get('/clear')
def clear():
    deleted = RepoModel.query.delete()
    return {'deleted': deleted}


def answer_question(repo_id, question):
    try:
        path = INDEXES / RepoModel.get_repo_path(repo_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Repo not found.") from e
    
    if not Path(path).exists():
        raise HTTPException(status_code=500, detail="Could not load index")

    with open(path, "rb") as f:
        index = pickle.load(f)

    chat_engine = index.as_chat_engine(chat_mode="context", verbose=True)

    response = chat_engine.chat(question)
    print(response)
    
    return response.response


def show():
    print(RepoModel.show_all())