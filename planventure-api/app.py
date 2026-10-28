import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from extensions import db

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY", "planventure-development-secret-key"
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///planventure.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app, origins=os.getenv("CORS_ORIGINS", "http://localhost:3000"))

db.init_app(app)
jwt = JWTManager(app)

from models import User  # noqa: E402, F401


@app.route("/")
def home():
    return jsonify({"message": "Welcome to PlanVenture API"})


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=True)