import json
import os
import base64
from flask import Flask, redirect, url_for, session, render_template, request, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json
from functools import wraps
from sqlalchemy.orm import Session

from gdrive_loader.db import engine
from gdrive_loader.models import User, Document
from gdrive_loader.answer import answer_query
from gdrive_loader import SETTINGS
from gdrive_loader.background import load_documents_from_user

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Change this to a secure secret key

# ONLY FOR LOCAL DEV
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


CREDENTIALS = json.loads(
    base64.b64decode(SETTINGS.GOOGLE_CREDENTIALS_BASE64).decode("utf-8")
)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    return render_template("index.html", logged_in="email" in session)


@app.route("/login")
def login():
    # Load client secrets
    flow = Flow.from_client_config(
        CREDENTIALS,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )

    session["state"] = state
    return redirect(authorization_url)


@app.route("/oauth2callback")
def oauth2callback():
    flow = Flow.from_client_config(
        CREDENTIALS,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
    )

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # Get user email
    service = build("oauth2", "v2", credentials=credentials)
    user_info = service.userinfo().get().execute()
    email = user_info["email"]

    # Store complete token information including refresh token
    token_info = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "expiry": credentials.expiry.isoformat(),
    }

    # Store or update user credentials
    with Session(engine) as db_session:
        user = db_session.query(User).filter_by(email=email).first()
        if user is None:
            user = User(email=email, token_info=json.dumps(token_info))
            db_session.add(user)
        else:
            user.token_info = json.dumps(token_info)

        db_session.commit()

    session["email"] = email
    return redirect(url_for("index"))


@app.post("/search")
def search_post():
    query = request.form["query"]
    answer = answer_query(query, email=session["email"])
    return render_template("search-results.html", answer=answer)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.get("/documents")
@login_required
def documents():
    email = session["email"]

    with Session(engine) as db_session:
        user = db_session.query(User).filter_by(email=email).first()
        documents = db_session.query(Document).filter_by(user_id=user.id).all()

    return render_template("documents.html", documents=documents, logged_in=True)


@app.post("/load")
@login_required
def load():
    email = session["email"]
    load_documents_from_user.delay(email, limit=50)
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True,
    )

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
