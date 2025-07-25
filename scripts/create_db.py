import os
from getpass import getpass

from parking_app_24f1002340.config import Config
from parking_app_24f1002340.parking import create_app
from parking_app_24f1002340.parking.extensions import db
from parking_app_24f1002340.parking.models import User

# Ensure imports work whether run from root or scripts folder
try:
    from parking.models import User  # noqa
except Exception:
    pass

def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Seed admin
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

        admin = User(username=admin_username, role="admin")
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()

        print("Database initialized.")
        print(f"Admin user created -> username: {admin_username}, password: {admin_password}")


if __name__ == "__main__":
    main()