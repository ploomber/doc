from os import environ


from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import stripe

import db

app = Flask(__name__)
app.secret_key = "your_secret_key"
stripe.api_key = environ.get("STRIPE_SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    with db.Session(db.engine) as session:
        return session.query(db.User).filter_by(id=user_id).first()


@app.route("/")
def home():
    subscription_message = ""
    if current_user.is_authenticated:
        if current_user.stripe_subscription_id:
            subscription_message = (
                "You have an active subscription. Enjoy our premium content!"
            )
        else:
            subscription_message = "You don't have an active subscription. Subscribe now to access premium content!"
    return render_template("home.html", subscription_message=subscription_message)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        with db.Session(db.engine) as session:
            user = session.query(db.User).filter_by(email=email).first()

        if user:
            flash("Email already exists", "error")
            return redirect(url_for("register"))

        with db.Session(db.engine) as session:
            new_user = db.User(email=email, password=generate_password_hash(password))
            session.add(new_user)
            session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        with db.Session(db.engine) as session:
            user = session.query(db.User).filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": environ.get("STRIPE_PRICE_ID"),
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=url_for("success", _external=True),
            cancel_url=url_for("home", _external=True),
            client_reference_id=str(current_user.id),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return str(e)


@app.route("/success")
def success():
    flash("Your subscription has been activated!", "success")
    return redirect(url_for("home"))


@app.route("/webhook", methods=["POST"])
def webhook():
    print("Webhook received")
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, environ.get("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        print("Invalid payload")
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        print("Invalid signature")
        return "Invalid signature", 400

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["client_reference_id"]
        subscription_id = session["subscription"]
        db.set_stripe_subscription_id(user_id, subscription_id)

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        db.set_stripe_subscription_id(user_id, None)

    return "", 200


@app.route("/free", methods=["POST"])
@login_required
def free_content():
    return "This is free content available to all users."


@app.route("/premium", methods=["POST"])
@login_required
def premium_content():
    if current_user.stripe_subscription_id:
        return (
            "This is premium content for subscribed users. Enjoy your exclusive access!"
        )
    else:
        return "Sorry, this content is only available to subscribed users. Please subscribe to access premium content."
