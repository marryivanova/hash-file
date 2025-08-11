import secrets

from flask import Flask
from flask_restx import Api
from flask_restx import fields, Namespace
from flask_jwt_extended import JWTManager

app = Flask(__name__)
key = secrets.token_urlsafe(32)
app.config["JWT_SECRET_KEY"] = key
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
jwt = JWTManager(app)

authorizations = {
    "Bearer Auth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Type in the *Value* input box: **Bearer &lt;JWT&gt;**",
    }
}

api = Api(
    app,
    version="1.0",
    title="File Storage API",
    description="API for uploading, downloading and managing files",
    doc="/swagger/",
    authorizations=authorizations,
    security="Bearer Auth",
)

auth_ns = Namespace("auth", description="Authentication operations")
file_ns = Namespace("file", description="File operations")

login_model = api.model(
    "Login",
    {
        "username": fields.String(required=True, description="Username"),
        "password": fields.String(required=True, description="Password"),
    },
)

file_upload_model = api.model(
    "FileUpload",
    {"file": fields.Raw(required=True, description="File to upload", type="file")},
)

file_response_model = api.model(
    "FileResponse", {"hash": fields.String(description="File hash")}
)

error_model = api.model("Error", {"error": fields.String(description="Error message")})
