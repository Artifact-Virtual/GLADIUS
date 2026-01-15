"""Module for Flask application with CORS support and a single home route."""

from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    """Render the home page."""
    return render_template("artifact_source2.html")


if __name__ == "__main__":
    app.run(debug=True)
