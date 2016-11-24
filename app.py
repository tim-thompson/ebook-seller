# Imports
from flask import Flask, render_template, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy

# App initialisation
app = Flask(__name__)
db = SQLAlchemy(app)


# Purchase model
class Purchase(db.Model):
    __tablename__ = "purchases"
    uuid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    downloads_left = db.Column(db.Integer)


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/purchase", methods=["POST"])
def purchase():
    return "purchase"


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
    app.run()
    db.create_all()
