import os
import hashlib
from flask import request, send_file, Response

from flask_restx import Resource
from flask import Blueprint, send_from_directory
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from src.app.docs_api import (
    auth_ns,
    login_model,
    file_response_model,
    error_model,
    file_ns,
)
from src.db.models import User, File
from src.db.data_base import SessionLocal
from src.utils.custom_logger import get_logger
from src.app._access_owner import file_owner_required
from src.app.file_dir import get_file_path, allowed_file

logger = get_logger(__name__)
logger.propagate = False


auth_bp = Blueprint("auth", __name__)
file_bp = Blueprint("file", __name__)


@auth_ns.route("/login")
class Login(Resource):
    """Handles user authentication and JWT token generation"""

    @auth_ns.expect(login_model)
    @auth_ns.response(200, "Success", file_response_model)
    @auth_ns.response(401, "Unauthorized", error_model)
    def post(self) -> tuple[dict[str, str], int]:
        """Authenticate user and return JWT token

        Returns:
            tuple: Contains either the access token or error message with status code
        """
        logger.info("Login attempt received")

        if not request.is_json:
            logger.warning("Invalid content type in login request")
            return {"error": "Content-Type must be application/json"}, 415

        data = request.get_json()

        if data is None:
            logger.warning("Invalid JSON data in login request")
            return {"error": "Invalid JSON data"}, 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            logger.warning("Missing username or password in login request")
            return {"error": "Username and password required"}, 400

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                logger.warning(f"Login failed - user not found: {username}")
                return {"error": "User not found"}, 401

            if not user.check_password(password):
                logger.warning(f"Invalid password for user: {username}")
                return {"error": "Invalid password"}, 401

            access_token = create_access_token(identity=username)
            logger.info(f"Successful login for user: {username}")
            return {"access_token": access_token}, 200
        finally:
            db.close()
            logger.debug("Database session closed for login request")


@file_ns.route("/protected")
class Protected(Resource):
    """Test endpoint for JWT verification"""

    @jwt_required()
    @file_ns.response(200, "Success")
    def get(self) -> dict[str, str]:
        """Verify JWT token is valid

        Returns:
            dict: Success message if JWT is valid
        """
        current_user = get_jwt_identity()
        logger.debug(f"JWT verification successful for user: {current_user}")
        return {"message": "JWT protected"}


@file_ns.route("/upload")
class FileUpload(Resource):
    """Handles file uploads to the server"""

    @jwt_required()
    @file_ns.doc(security="Bearer Auth")
    @file_ns.param("file", "File to upload", "formData", type="file", required=True)
    def post(self) -> tuple[dict[str, str], int]:
        """Upload a file to the server

        Returns:
            tuple: Contains either the file hash or error message with status code
        """
        current_user = get_jwt_identity()
        logger.info(f"File upload attempt by user: {current_user}")

        if "file" not in request.files:
            logger.warning("No file part in upload request")
            return {"error": "No file part"}, 400

        file = request.files["file"]
        if file.filename == "":
            logger.warning("Empty filename in upload request")
            return {"error": "No selected file"}, 400

        if not allowed_file(file.filename):
            logger.warning(f"Disallowed file type attempted: {file.filename}")
            return {"error": "File type not allowed"}, 400

        try:
            file_data = file.read()
            file_hash = hashlib.sha256(file_data).hexdigest()
            file_path = get_file_path(file_hash)

            if os.path.exists(file_path):
                logger.info(f"File already exists, hash: {file_hash}")
                return {"error": "File already exists"}, 409

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(file_data)
            logger.debug(f"File saved to disk at: {file_path}")

            db = SessionLocal()
            try:
                user = db.query(User).filter_by(username=current_user).first()
                new_file = File(hash=file_hash, user_id=user.id)
                db.add(new_file)
                db.commit()
                logger.info(f"File record created in DB, hash: {file_hash}")
                return {"hash": file_hash}, 201
            except Exception as db_error:
                db.rollback()
                logger.error(f"Database error during file upload: {str(db_error)}")
                return {"error": "Database operation failed"}, 500
            finally:
                db.close()
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            return {"error": str(e)}, 500


@file_ns.route("/download/<string:file_hash>")
class FileDownload(Resource):
    """Handles file downloads with owner verification and secure file delivery"""

    @jwt_required()
    @file_ns.doc(
        security="Bearer Auth",
        responses={
            200: "File downloaded successfully",
            404: "File not found",
            500: "Internal server error",
        },
    )
    @file_ns.param("file_hash", "SHA256 hash of the file to download")
    @file_owner_required
    def get(
        self, file_hash: str, file_record: dict, file_path: str
    ) -> tuple[dict[str, str], int] | Response:
        """Download a file after verifying ownership

        Args:
            file_hash: SHA256 hash of the requested file
            file_record: File record from database (provided by decorator)
            file_path: Absolute path to file on disk (provided by decorator)

        Returns:
            Response: File as attachment with proper headers or error message
        """
        current_user = get_jwt_identity()
        logger.info("Download request for file %s by user %s", file_hash, current_user)

        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found on disk: {file_path}")
                return {"error": "File not found on disk"}, 404

            try:
                logger.debug(f"Attempting to send file from directory: {file_path}")
                return send_from_directory(
                    directory=os.path.dirname(file_path),
                    path=os.path.basename(file_path),
                    as_attachment=True,
                    download_name=f"file_{file_hash[:8]}",
                )
            except Exception as e:
                logger.warning(f"Fallback to send_file for {file_path}: {str(e)}")
                return send_file(
                    file_path, as_attachment=True, download_name=f"file_{file_hash[:8]}"
                )
        except Exception as e:
            logger.error(f"Download failed for {file_hash}: {str(e)}")
            return {"error": f"Download failed: {str(e)}"}, 500


@file_ns.route("/delete/<string:file_hash>")
class FileDelete(Resource):
    """Handles file deletion with owner verification"""

    @jwt_required()
    @file_ns.doc(security="Bearer Auth")
    @file_owner_required
    @file_ns.response(200, "Success")
    @file_ns.response(403, "Forbidden")
    @file_ns.response(404, "Not Found")
    @file_ns.response(500, "Server Error")
    def delete(self, file_hash, file_record, file_path) -> tuple[dict[str, str], int]:
        """Delete a file after verifying ownership

        Args:
            file_hash: SHA256 hash of the file to delete
            file_record: File record from database (provided by decorator)
            file_path: Path to file on disk (provided by decorator)

        Returns:
            tuple: Success message or error with status code
        """
        current_user = get_jwt_identity()
        logger.info(f"Delete request for file {file_hash} by user {current_user}")

        db = SessionLocal()
        try:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"File deleted from disk: {file_path}")
            except OSError as e:
                logger.error(f"Failed to delete file from disk: {str(e)}")
                return {"error": f"Failed to delete file from disk: {str(e)}"}, 500

            db.delete(file_record)
            db.commit()
            logger.info(f"File record deleted from DB, hash: {file_hash}")

            return {"message": "File deleted successfully"}, 200
        except Exception as e:
            db.rollback()
            logger.error(f"File deletion failed: {str(e)}")
            return {"error": str(e)}, 500
        finally:
            db.close()
            logger.debug("Database session closed for delete operation")
