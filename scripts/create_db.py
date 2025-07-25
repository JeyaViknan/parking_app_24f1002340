import os
import sys

# Ensure the project root is on sys.path when running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parking import create_app
from parking.extensions import db
from parking.models import User


def main():
    app = create_app()  # <-- no arguments
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Seed admin
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

        if not User.query.filter_by(username=admin_username).first():
            admin = User(username=admin_username, role="admin")
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created: username={admin_username}, password={admin_password}")
        else:
            print("Admin user already exists.")


if __name__ == "__main__":
    main()
