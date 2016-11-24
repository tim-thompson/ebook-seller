from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()

class Purchase(db.table):
    __tablename__ = "purchases"
    uuid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    downloads_left = db.Column(db.Integer)