"""Flask application factory."""

from pathlib import Path
from flask import Flask

from src.config import Config


def create_app() -> Flask:
    """Create and configure the Flask app."""
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).resolve().parent.parent / "templates"),
        static_folder=str(Path(__file__).resolve().parent.parent / "static"),
    )
    app.config.from_object(Config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["OUTPUT_FOLDER"]).mkdir(parents=True, exist_ok=True)

    from app.routes import main_bp

    app.register_blueprint(main_bp)
    return app
