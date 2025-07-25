from flask import Flask
from flask_login import LoginManager
from .extensions import db, login_manager
from .models import User
from .auth.routes import auth_bp
from .admin.routes import admin_bp
from .user.routes import user_bp
from .models import ParkingLot, ParkingSpot, Reservation


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_bp, url_prefix="/user")

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()  # Ensure tables exist if not using create_db.py

    return app
