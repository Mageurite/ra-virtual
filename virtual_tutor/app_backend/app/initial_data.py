from app.core.config import settings
from app.db.session import Base, engine, SessionLocal
from app.models.admin import Admin
from app.core.security import get_password_hash


def create_initial_admin():
    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(Admin.email == settings.INIT_ADMIN_EMAIL).first()
        if existing:
            print(f"Admin already exists: {existing.email}")
            return

        admin = Admin(
            email=settings.INIT_ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.INIT_ADMIN_PASSWORD),
        )
        db.add(admin)
        db.commit()
        print(f"Created initial admin: {admin.email}")
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    create_initial_admin()
