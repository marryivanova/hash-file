import os

from flask import jsonify
from functools import wraps
from flask_jwt_extended import get_jwt_identity

from src.db.models import File, User
from src.app.file_dir import get_file_path
from src.db.data_base import SessionLocal
from src.utils.custom_logger import get_logger

logger = get_logger(__name__)
logger.propagate = False


def file_owner_required(f):
    """
    Decorator to verify that the current user is the owner of the requested file.

    This decorator checks:
    1. If the file hash is provided
    2. If the current user exists
    3. If the file exists and belongs to the current user
    4. If the file exists on disk

    Args:
        f (function): The route function to be decorated

    Returns:
        function: The decorated function with additional file verification
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        logger.info(f"Starting file owner verification for request")

        file_hash = kwargs.get("file_hash")
        if not file_hash:
            logger.error("File hash not provided in request")
            return jsonify({"error": "File hash not provided"}), 400

        current_user = get_jwt_identity()
        logger.debug(f"Verifying file ownership for user: {current_user}")

        db = SessionLocal()
        try:
            user = db.query(User).filter_by(username=current_user).first()
            if not user:
                logger.error(f"User not found in database: {current_user}")
                return jsonify({"error": "User not found"}), 404

            file_record = (
                db.query(File).filter_by(hash=file_hash, user_id=user.id).first()
            )

            if not file_record:
                logger.warning(
                    f"File not found or access denied. "
                    f"User: {current_user}, File hash: {file_hash}"
                )
                return jsonify({"error": "File not found or access denied"}), 403

            file_path = get_file_path(file_hash)
            if not file_path or not os.path.exists(file_path):
                logger.error(
                    f"File not found on disk. "
                    f"File hash: {file_hash}, Expected path: {file_path}"
                )
                return jsonify({"error": "File not found on disk"}), 404

            logger.info(
                f"File ownership verified successfully. "
                f"User: {current_user}, File hash: {file_hash}"
            )

            kwargs["file_record"] = file_record
            kwargs["file_path"] = file_path
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Unexpected error during file verification: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
        finally:
            db.close()
            logger.debug("Database session closed")

    return decorated
