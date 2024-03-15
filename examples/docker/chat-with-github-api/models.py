from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, desc
from sqlalchemy.orm import relationship
import humanize

from database import Base, engine


class ModelMixin:
    """Provides common functionality for all models."""

    @property
    def created_natural(self):
        return humanize.naturaltime(datetime.utcnow() - self.created)


class RepoModel(ModelMixin, Base):
    __tablename__ = "repos"

    id = Column(String, primary_key=True)
    status = Column(String(120), default="pending")
    path = Column(String(120))

    def __repr__(self):
        return f"<Repo {self.id!r}, {self.status!r}, {self.path!r}>"

    @classmethod
    def get_repo_status(cls, repo_id):
        repo = cls.query.filter_by(id=repo_id).first()
        return repo.status
    
    @classmethod
    def update_repo_status(cls, repo_id, status):
        repo = cls.query.filter_by(id=repo_id).first()
        repo.status = status
        return repo.status
    
    @classmethod
    def show_all(cls):
        return cls.query.filter().all()


if __name__ == "__main__":
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
