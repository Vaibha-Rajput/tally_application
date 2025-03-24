from flask import Flask
from app.routes import ledger_bp

def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object("config.Config")
    app.register_blueprint(ledger_bp)
    return app
