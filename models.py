import sqlalchemy as sa
import sqlalchemy.orm as so
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timezone
from typing import Optional
from werkzeug.security import generate_password_hash

engine = sa.create_engine("sqlite:///data.db")
Session = so.sessionmaker(bind=engine)
session = Session()

def init_db():
    if not os.path.exists('data.db'):
        print("Database initialize...")
        Base.metadata.create_all(engine)

class Base(so.DeclarativeBase):
    pass


class User(Base):

    __tablename__ = "user"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(60), unique=True)
    master_password: so.Mapped[str] = so.mapped_column(sa.String(120))
    salt: so.Mapped[bytes] = so.mapped_column(sa.BLOB, unique=True)
    apps: so.WriteOnlyMapped['App'] = so.relationship(back_populates='users', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.master_password = generate_password_hash(password)

    def set_salt(self):
        self.salt = os.urandom(16)

    def generate_key(self, password):
        salt = self.salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1_200_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def get_apps(self):
        apps = session.scalars(self.apps.select()).all()

        return {
            'id': [app.id for app in apps],
            'url': [app.url for app in apps],
            'name': [app.name for app in apps],
            'password': [app.password for app in apps]
        }

class App(Base):

    __tablename__ = "app"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'))
    name: so.Mapped[str] = so.mapped_column(sa.String(60))
    username: so.Mapped[str] = so.mapped_column(sa.String(60))
    password: so.Mapped[str] = so.mapped_column(sa.String(120))
    url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120), nullable=True)
    date_created: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    users: so.Mapped[User] = so.relationship(back_populates='apps')

    def __repr__(self):
        return f"<App {self.name}>"
