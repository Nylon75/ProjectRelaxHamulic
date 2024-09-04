from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import os

from config import Config
from extensions import db, migrate, mail, login_manager
from models import User, Review
from routes import init_routes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_login'

    CORS(app)
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Initialize routes
    init_routes(app)

    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('Krajina1412')
            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)