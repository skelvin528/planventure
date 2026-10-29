from functools import wraps
from typing import Callable

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import User


def login_required(view: Callable) -> Callable:
    @wraps(view)
    @jwt_required()
    def protected_view(*args, **kwargs):
        return view(*args, **kwargs)

    return protected_view


def get_current_user() -> User | None:
    user_id = get_jwt_identity()
    if user_id is None:
        return None
    return User.query.get(int(user_id))
