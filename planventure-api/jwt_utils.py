from flask_jwt_extended import create_access_token, decode_token
from flask_jwt_extended.exceptions import JWTDecodeError
from jwt import ExpiredSignatureError, InvalidTokenError


def generate_access_token(user_id: int) -> str:
    return create_access_token(identity=str(user_id))


def validate_access_token(token: str) -> int | None:
    try:
        identity = decode_token(token)["sub"]
        return int(identity)
    except (
        JWTDecodeError,
        ExpiredSignatureError,
        InvalidTokenError,
        TypeError,
        ValueError,
    ):
        return None
