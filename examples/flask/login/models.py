import secrets
from datetime import datetime
import hashlib


from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, desc
from sqlalchemy.orm import relationship
import humanize
import bcrypt

from database import Base, engine


class ModelMixin:
    """Provides common functionality for all models."""

    @property
    def created_natural(self):
        return humanize.naturaltime(datetime.utcnow() - self.created)


class APICall(ModelMixin, Base):
    __tablename__ = "api_calls"

    id = Column(Integer, primary_key=True)

    created = Column(DateTime, default=datetime.utcnow)
    event_name = Column(String(120))

    user_id = Column(Integer, ForeignKey("users.id"))


class APIKey(ModelMixin, Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.utcnow)

    name = Column(String(120))
    key = Column(String(120), unique=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    def __init__(self, *, user_id, name, key):
        self.user_id = user_id
        self.name = name
        self.key = key
        self.key_raw = None

    @classmethod
    def new_for_user_with_id(cls, *, name, user_id):
        api_key_raw = secrets.token_urlsafe()
        api_key_hashed = hashlib.sha256(api_key_raw.encode()).hexdigest()
        obj = cls(user_id=user_id, name=name, key=api_key_hashed)
        obj.key_raw = api_key_raw
        return obj

    @classmethod
    def get_with_key(cls, key):
        hashed_key = hashlib.sha256(key.encode()).hexdigest()
        return cls.query.filter_by(key=hashed_key).first()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True)
    password = Column(String(120))

    api_calls = relationship("APICall", backref="user", order_by=desc(APICall.created))
    api_keys = relationship("APIKey", backref="user", order_by=desc(APIKey.created))

    def __repr__(self):
        return f"<User {self.email!r}>"

    @classmethod
    def with_password(cls, *, email, password):
        salt = bcrypt.gensalt()
        password_hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return cls(email=email, password=password_hashed)

    @classmethod
    def get_by_password(cls, *, email, password):
        user = cls.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode("utf-8"), user.password):
            return user
        return None

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
