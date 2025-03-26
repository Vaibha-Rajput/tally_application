from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database


from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "..", "templates")


def create_database_if_not_exists(uri):
    """Check if the database exists, and create it if not."""
    engine = create_engine(uri)  # Create engine instance
    if not database_exists(engine.url):  # Check if DB exists
        create_database(engine.url)  # Create database
        print(f"Database '{engine.url.database}' created successfully.")
    else:
        print(f"Database '{engine.url.database}' already exists.")

def create_app():
    create_database_if_not_exists(Config.SQLALCHEMY_DATABASE_URI)
    app = Flask(__name__, template_folder=TEMPLATE_DIR)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import models here to avoid circular import issues
        from app import models
        db.create_all()  # Ensures tables are created if they don't exist

    # Import and register blueprints after db is initialized
    from app.routes import ledger_bp
    app.register_blueprint(ledger_bp)

    return app
