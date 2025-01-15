from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Text,
    func,
    CheckConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator, BLOB
from sqlite_vec import serialize_float32
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
import enum


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class FloatArray(TypeDecorator):
    """Custom type for SQLite float array stored as BLOB"""

    impl = BLOB
    cache_ok = True

    def process_bind_param(self, value, dialect):
        # Convert float array to BLOB when saving
        if value is None:
            return None
        return serialize_float32(value)

    def process_result_value(self, value, dialect):
        # Convert BLOB back to float array when loading
        if value is None:
            return None
        return value


class DocumentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    embedding: Mapped[bytes] = mapped_column(FloatArray, nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(nullable=False)

    __table_args__ = (
        CheckConstraint(
            "embedding IS NULL OR (typeof(embedding) = 'blob' AND vec_length(embedding) = 1536)",
            name="check_embedding_type_and_length",
        ),
    )

    @classmethod
    def find_similar(cls, session, embedding, limit: int = None):
        query = text(
            """
            SELECT id, vec_distance_L2(embedding, :embedding) as distance
            FROM documents
            ORDER BY distance
            """
            + (f"LIMIT {limit}" if limit else "")
        )

        result = session.execute(query, {"embedding": serialize_float32(embedding)})

        # Fetch the actual Document objects and pair them with their distances
        documents_with_distances = []
        for row in result:
            document = session.get(cls, row.id)
            documents_with_distances.append(document)

        return documents_with_distances
