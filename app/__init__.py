import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Enable detailed error logging
    app.config['DEBUG'] = True  # Set to False in production
    app.config['PROPAGATE_EXCEPTIONS'] = True  # Propagate exceptions to the log

    # Set database URI from environment variable
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    if not app.config['SQLALCHEMY_DATABASE_URI']:
        raise RuntimeError("DATABASE_URL environment variable is not set!")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-fallback-key')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Add user loader
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register routes
    from app.routes import bp
    app.register_blueprint(bp)

    # Initialize blockchain and database
    with app.app_context():
        from app.blockchain import Blockchain
        app.blockchain = Blockchain()  # Initialize blockchain
        db.create_all()  # Create database tables

    return app

# Create app instance
app = create_app()