import requests
import os

API_ROOT = os.environ.get("API_ROOT") or "http://0.0.0.0:8765"

def status_color(status):
    match status:
        case "finished":
            return "green"
        case "pending":
            return "black"
        case "failed":
            return "red"

def _process_response(response):
        """Process response and raise an exception if the status code is not 200"""
        if response.ok:
            return True, response.json()
        else:
            error_message = response.json()["detail"]
            raise ValueError(error_message)

def index():
    response = requests.get(
            f"{API_ROOT}/",
            headers={
                "Content-Type": "application/json",
            },
        )

    return response.json()["hello"]

def repos():
    response = requests.get(
            f"{API_ROOT}/repos",
            headers={
                "Content-Type": "application/json",
            },
        )

    success, content = _process_response(response)
    if success:
        return content["repos"]

def scrape(owner, name, branch):
    response = requests.post(
            f"{API_ROOT}/scrape",
            headers={
                "Content-Type": "application/json",
            },
            json={"owner": owner, "name": name, "branch": branch}
        )

    success, content = _process_response(response)
    if success:
        return content["id"]
    

def status(repo_id):
    response = requests.get(
            f"{API_ROOT}/status/{repo_id}",
            headers={
                "Content-Type": "application/json",
            },
        )

    success, content = _process_response(response)
    if success:
        return content["status"]

def ask(repo_id, q):
    response = requests.post(
            f"{API_ROOT}/ask",
            headers={
                "Content-Type": "application/json",
            },
            json={"repo_id": repo_id, "question": q}
        )

    success, content = _process_response(response)
    if success:
        return content["answer"], False
    else:
        return "", True
    

def reset():
    response = requests.get(
            f"{API_ROOT}/clear",
            headers={
                "Content-Type": "application/json",
            },
        )

    success, content = _process_response(response)
    if success:
        return content["deleted"] 