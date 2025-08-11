import os
from os.path import join, dirname
from dotenv import load_dotenv

from src.app.docs_api import app, api
from src.app.routers import auth_bp, file_bp, auth_ns, file_ns

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

api.add_namespace(auth_ns, path="/auth")
api.add_namespace(file_ns, path="/file")

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(file_bp, url_prefix="/file")

if __name__ == "__main__":
    app.run(
        host=str(os.getenv("APP_HOST")),
        port=int(os.getenv("APP_PORT")),
        debug=bool(os.getenv("APP_DEBUG")),
        use_reloader=True,
    )
