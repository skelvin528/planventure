import os
from datetime import timedelta

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
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///planventure.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")
    if origin.strip()
]
CORS(
    app,
    origins=cors_origins,
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
)

db.init_app(app)
jwt = JWTManager(app)

from models import User  # noqa: E402, F401
from auth import auth_bp
from trip_routes import trips_bp

app.register_blueprint(auth_bp)
app.register_blueprint(trips_bp)


@jwt.unauthorized_loader
def handle_missing_token(_error):
    return jsonify({"error": "Authentication token is required"}), 401


@jwt.invalid_token_loader
def handle_invalid_token(_error):
    return jsonify({"error": "Invalid authentication token"}), 401


@jwt.expired_token_loader
def handle_expired_token(_jwt_header, _jwt_payload):
    return jsonify({"error": "Authentication token has expired"}), 401


@app.route("/")
def home():
    return jsonify({"message": "Welcome to PlanVenture API"})


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=True)