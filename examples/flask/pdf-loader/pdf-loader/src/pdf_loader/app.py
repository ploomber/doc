from flask import (
    Flask,
    redirect,
    url_for,
    session,
    render_template,
    request,
    flash,
)
from functools import wraps
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pdf_loader.db import engine
from pdf_loader.models import User, Document, DocumentStatus
from pdf_loader.answer import answer_query
from pdf_loader.background import process_pdf_document
from pdf_loader import SETTINGS

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Change this to a secure secret key


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
@login_required
def index():
    return render_template("index.html", logged_in=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        with Session(engine) as db_session:
            user = db_session.query(User).filter_by(email=email).first()

            if user and user.check_password(password):
                session["email"] = user.email
                return redirect(url_for("index"))

            flash("Invalid email or password", "error")
            return render_template("login.html", logged_in=False, email=email)

    return render_template("login.html", logged_in=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html", logged_in=False)

        with Session(engine) as db_session:
            try:
                user = User(email=email)
                user.set_password(password)
                db_session.add(user)
                db_session.commit()

                session["email"] = user.email
                return redirect(url_for("index"))
            except IntegrityError:
                db_session.rollback()
                flash("Email already registered", "error")

    return render_template("register.html", logged_in=False)


@app.post("/search")
@login_required
def search_post():
    query = request.form["query"]
    answer = answer_query(query)
    return render_template("search-results.html", answer=answer)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("index"))


@app.get("/documents")
@login_required
def documents():
    with Session(engine) as db_session:
        documents = db_session.query(Document).all()

    return render_template("documents.html", documents=documents, logged_in=True)


@app.post("/upload")
@login_required
def upload():
    if "files[]" not in request.files:
        flash("No files uploaded", "error")
        return redirect(url_for("documents"))

    files = request.files.getlist("files[]")
    if not files or all(f.filename == "" for f in files):
        flash("No files selected", "error")
        return redirect(url_for("documents"))

    upload_dir = SETTINGS.PATH_TO_UPLOADS
    uploaded = 0

    with Session(engine) as db_session:
        for file in files:
            if not file.filename.lower().endswith(".pdf"):
                flash(f"Skipping {file.filename} - only PDF files are allowed", "error")
                continue

            # Save the uploaded file
            file_path = upload_dir / file.filename
            file.save(file_path)

            # Create document record
            document = Document(
                name=file.filename,
                status=DocumentStatus.PENDING,
            )
            db_session.add(document)
            uploaded += 1

        if uploaded > 0:
            db_session.commit()
            # Start processing tasks for all uploaded documents
            for file in files:
                if file.filename.lower().endswith(".pdf"):
                    process_pdf_document.delay(file.filename)

    if uploaded == 0:
        flash("No valid PDF files were uploaded", "error")
    elif uploaded == 1:
        flash("File uploaded successfully", "success")
    else:
        flash(f"{uploaded} files uploaded successfully", "success")

    return redirect(url_for("documents"))


if __name__ == "__main__":
    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True,
    )

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
