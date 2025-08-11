from functools import wraps
from flask import request

from src.db.models import User
from src.utils.custom_logger import get_logger


logger = get_logger(__name__)
logger.propagate = False


def check_auth(username: str, password: str) -> bool:
    """Verify user credentials."""
    user = User.query.filter_by(username=username).first()
    return user is not None and user.verify_password(password)


def auth_required(f):
    """Decorator for basic authentication."""

    @wraps(f)
    def decorated(*args, **kwargs) -> tuple[dict[str, str], int]:
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return {"error": "Invalid credentials"}, 401
        if not check_auth(auth.username, auth.password):
            return {"error": "Invalid credentials"}, 401
        return f(*args, **kwargs)

    return decorated
