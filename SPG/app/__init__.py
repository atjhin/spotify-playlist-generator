from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt



# Initialize SQLAlchemy
db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../instance/config.py')  # Load configuration

    # Initialize the database
    db.init_app(app)

    # Import models so they are registered with SQLAlchemy
    from app import database

    # Register blueprints (if any)
    with app.app_context():
        from .routes import main_blueprint
        app.register_blueprint(main_blueprint)

    return app
