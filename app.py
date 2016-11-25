# Imports
from flask import Flask, render_template, abort, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from threading import Thread
import stripe
import uuid

# App initialisation
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
db = SQLAlchemy(app)
app.config["MAIL_SERVER"] = "smtp.google.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "username"
app.config["MAIL_PASSWORD"] = "password"
mail = Mail(app)

stripe_keys = {
    "secret_key": "sk_test_5WBtu8XKaANm4aeEImkEP6nO",
    "publishable_key": "pk_test_jXjLvVkpCCkbNksMR4atuIpf"
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
