from flask import jsonify
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token

from src.app._access_owner import file_owner_required


def test_file_owner_required_missing_hash(app):
    @app.route("/test/<file_hash>")
    @file_owner_required
    def test_route(file_hash):
        return jsonify({"success": True})

    with app.test_client() as client:
        response = client.get("/test/")
        assert response.status_code == 404


def test_file_owner_required_success(app):
    with app.app_context():
        access_token = create_access_token(identity="test_user")

    @app.route("/test/<file_hash>")
    @file_owner_required
    def test_route(file_hash, file_record, file_path):
        return jsonify({"success": True, "file_hash": file_hash})

    with patch("src.app._access_owner.SessionLocal") as mock_db, patch(
        "src.app._access_owner.os.path.exists"
    ) as mock_exists, patch(
        "src.app._access_owner.get_file_path"
    ) as mock_get_path, patch(
        "src.app._access_owner.get_jwt_identity"
    ) as mock_jwt:

        mock_session = MagicMock()
        mock_db.return_value = mock_session
        mock_jwt.return_value = "test_user"

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "test_user"

        mock_file = MagicMock()
        mock_file.hash = "valid_hash"
        mock_file.user_id = 1

        user_query = MagicMock()
        user_query.first.return_value = mock_user

        file_query = MagicMock()
        file_query.first.return_value = mock_file

        mock_session.query.side_effect = [user_query, file_query]

        mock_exists.return_value = True
        mock_get_path.return_value = "/path/to/file"

        with app.test_client() as client:
            response = client.get(
                "/test/valid_hash", headers={"Authorization": f"Bearer {access_token}"}
            )

            assert response.status_code == 200
            assert response.json == {"success": True, "file_hash": "valid_hash"}
