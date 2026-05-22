from sqlalchemy.orm import Session
from app.models import User
from app.auth.security import hash_password

def seed_defaults(db: Session):
    defaults = [
        ("admin", "admin@lab.local", "Admin", "admin", "Admin@123", True),
        ("signer1", "signer1@lab.local", "Signer One", "signer", "Signer@123", False),
        ("signer2", "signer2@lab.local", "Signer Two", "signer", "Signer@123", False),
    ]
    for username, email, dn, role, pwd, must in defaults:
        if not db.query(User).filter(User.username == username).first():
            db.add(User(username=username, email=email, display_name=dn, role=role, password_hash=hash_password(pwd), must_change_password=must))
    db.commit()
