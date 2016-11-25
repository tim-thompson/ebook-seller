# Imports
from flask import Flask, render_template, abort, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from threading import Thread
import stripe, uuid, json


# App initialisation
app = Flask(__name__)
db = SQLAlchemy(app)
mail = Mail(app)

# Load Config
with open("config.json", "r") as f:
    config = json.load(f)

app.config["SQLALCHEMY_DATABASE_URI"] = config["db_address"]
app.config["MAIL_SERVER"] = config["mail"]["server"]
app.config["MAIL_PORT"] = config["mail"]["port"]
app.config["MAIL_USE_TLS"] = config["mail"]["tls"]
app.config["MAIL_USERNAME"] = config["mail"]["username"]
app.config["MAIL_PASSWORD"] = config["mail"]["password"]

stripe_keys = {
    "secret_key": config["stripe"]["secret_key"],
    "publishable_key": config["stripe"]["publishable_key"]
}

stripe.api_key = stripe_keys["secret_key"]


# Purchase model
class Purchase(db.Model):
    __tablename__ = "purchases"
    uuid = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    downloads_left = db.Column(db.Integer, default=5)


# Routes
@app.route("/")
def index():
    return render_template("index.html", key=stripe_keys["publishable_key"])


@app.route("/purchase", methods=["POST"])
def purchase():
    amount = 499

    customer = stripe.Customer.create(
        email=request.form["stripeEmail"],
        source=request.form["stripeToken"]
    )

    charge = stripe.Charge.create(
        amount=amount,
        currency="gbp",
        customer=customer.id,
        description="E-Book purchase"
    )

    purchase = Purchase(uuid=str(uuid.uuid4()), email=request.form["stripeEmail"])
    send_email(request.form["stripeEmail"], "Your Download is Ready", uuid=purchase.uuid)

    print(purchase.uuid)
    db.session.add(purchase)
    db.session.commit()

    return render_template("charge.html", amount=amount)


@app.route("/<uuid>")
def download(uuid):
    purchase = Purchase.query.get(uuid)
    if purchase:
        if purchase.downloads_left <= 0:
            return "You have no downloads left"
        else:
            purchase.downloads_left -= 1
            db.session.commit()
            print(purchase.downloads_left)
            return send_from_directory("downloads", "book.pdf")
    else:
        abort(404)


# Helper Functions
def send_email(to, subject, **kwargs):
    msg = Message("E-Book Download", sender="woo@tim.co.uk", recipients=[to])
    msg.body = render_template("download.txt", **kwargs)
    msg.html = render_template("download.html", **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# Main app
if __name__ == "__main__":
    db.create_all()
    app.run()
