# Imports
from flask import Flask, render_template, abort, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
import stripe

# App initialisation
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
db = SQLAlchemy(app)

stripe_keys = {
    "secret_key": "sk_test_5WBtu8XKaANm4aeEImkEP6nO",
    "publishable_key": "pk_test_jXjLvVkpCCkbNksMR4atuIpf"
}

stripe.api_key = stripe_keys["secret_key"]

# Purchase model
class Purchase(db.Model):
    __tablename__ = "purchases"
    uuid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    downloads_left = db.Column(db.Integer)


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
            return send_from_directory("downloads", "book.pdf")
    else:
        abort(404)


# Main app
if __name__ == "__main__":
    db.create_all()
    app.run()
