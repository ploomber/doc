from os import environ

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    current_user,
    login_required,
)


from database import db_session
from models import User, APIKey, APICall
import forms
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)

# this is required by flask-login
app.secret_key = environ["FLASK_SECRET_KEY"]

login_manager = LoginManager()
login_manager.init_app(app)

from functools import wraps


def rate_limit(func):
    """Decorator to rate limit API calls from anonymous users."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            n_api_calls = APICall.count_calls_for_user(user_id=current_user.id)

            error = (
                "You have exceeded the number of allowed API calls for "
                "anonymous users, please create an account!"
            )

            if n_api_calls >= 5:
                return {"error": error}, 429

        return func(*args, **kwargs)

    return wrapper


@login_manager.user_loader
def load_user(user_id):
    """
    Authenticate users when performing requests via the browser. Authentication
    management is handled by flask-login.
    """
    return User.get_by_id(user_id)


@login_manager.request_loader
def load_user_from_request(request):
    """
    Authenticate users when performing requests via the API. Authentication
    management haappens by checking the Authorization header.
    """
    authorization_header = request.headers.get("Authorization")

    if authorization_header and authorization_header.startswith("Bearer "):
        api_key = authorization_header.split(" ")[1]
        result = APIKey.get_with_key(key=api_key)

        if result:
            return User.get_by_id(result.user_id)

    return None


@app.route("/")
def home():
    server_name = request.host_url

    if server_name.endswith("/"):
        server_name = server_name[:-1]

    return render_template("home.html", user=current_user, server_name=server_name)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = forms.SignUpForm(request.form)

    if request.method == "POST" and form.validate():
        user = User.with_password(email=form.email.data, password=form.password.data)
        db_session.add(user)

        try:
            db_session.commit()
        except IntegrityError as e:
            app.logger.exception(e)
            db_session.rollback()
            flash("This email is already in use")
            return redirect(url_for("signup"))

        flash("Thanks for registering")
        return redirect(url_for("login"))

    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm(request.form)

    if request.method == "POST" and form.validate():
        user = User.get_by_password(email=form.email.data, password=form.password.data)

        if user:
            flash("Successfully logged in")
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/anonymous", methods=["POST"])
def anonymous():
    user = User()
    db_session.add(user)
    db_session.commit()

    login_user(user)
    flash("Logged in as anonymous user")
    return redirect(url_for("home"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("home"))


@app.route("/api/key", methods=["POST"])
@login_required
def api_key():
    name = request.json.get("name")
    api_key = APIKey.new_for_user_with_id(name=name, user_id=current_user.id)
    db_session.add(api_key)
    db_session.commit()
    return {"key": api_key.key_raw}


@app.route("/api/sum/<int:a>/<int:b>")
@rate_limit
@login_required
def api_sum(a, b):
    api_call = APICall(event_name="api_sum", user_id=current_user.id)
    db_session.add(api_call)
    db_session.commit()
    return {"result": a + b}


@app.route("/api/substract/<int:a>/<int:b>")
@rate_limit
@login_required
def api_substract(a, b):
    api_call = APICall(event_name="api_substract", user_id=current_user.id)
    db_session.add(api_call)
    db_session.commit()
    return {"result": a - b}


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
