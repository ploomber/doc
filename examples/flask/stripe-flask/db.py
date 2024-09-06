from uuid import uuid4


from flask_login import UserMixin
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class User(Base, UserMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(8), primary_key=True, default=lambda: uuid4().hex[:8]
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    stripe_subscription_id: Mapped[str] = mapped_column(String(255), nullable=True)

    def get_id(self):
        return str(self.id)


engine = create_engine("sqlite:///my.db")

Base.metadata.create_all(engine)


def set_stripe_subscription_id(user_id, subscription_id):
    with Session(engine) as db_session:
        user = db_session.query(User).filter_by(id=user_id).first()
        if user:
            user.stripe_subscription_id = subscription_id
            db_session.commit()
