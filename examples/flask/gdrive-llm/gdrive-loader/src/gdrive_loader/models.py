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
from sqlalchemy import text, ForeignKey


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    token_info: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


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


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[bytes] = mapped_column(FloatArray, nullable=True)
    google_drive_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "embedding IS NULL OR (typeof(embedding) = 'blob' AND vec_length(embedding) = 1536)",
            name="check_embedding_type_and_length",
        ),
    )

    @classmethod
    def find_similar(cls, session, embedding, user_id, limit: int = None):
        query = text(
            """
            SELECT id, vec_distance_L2(embedding, :embedding) as distance
            FROM documents
            WHERE user_id = :user_id
            ORDER BY distance
            """
            + (f"LIMIT {limit}" if limit else "")
        )

        result = session.execute(
            query, {"embedding": serialize_float32(embedding), "user_id": user_id}
        )

        # Fetch the actual Document objects and pair them with their distances
        documents_with_distances = []
        for row in result:
            document = session.get(cls, row.id)
            documents_with_distances.append(document)

        return documents_with_distances

    def to_markdown(self):
        return f"""
# {self.name}

{self.content}
"""
