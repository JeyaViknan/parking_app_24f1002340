from config import Config
from parking import create_app
from parking.extensions import db
from parking.models import User
from werkzeug.security import generate_password_hash

app = create_app(Config)

with app.app_context():
    db.drop_all()
    db.create_all()
    # Create admin user
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password_hash=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: username=admin, password=admin123")
    else:
        print("Admin user already exists.")
