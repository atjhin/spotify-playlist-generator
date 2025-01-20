from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import secrets 

db = SQLAlchemy()
SESSION_ID = secrets.token_hex(16)
def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../instance/config.py')

    # Initialize database with app
    db.init_app(app)

    # Flask-Session configuration
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = db
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.secret_key = 'your_secret_key'

    # Initialize Flask-Session
    Session(app)

    with app.app_context():
        from app.routes import main_blueprint
        app.register_blueprint(main_blueprint)

    return app
