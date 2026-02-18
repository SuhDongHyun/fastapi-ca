from database import Base
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Table, Column, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

note_tag_association = Table(
    "note_tag",
    Base.metadata,
    Column("note_id", String(36), ForeignKey("notes.id")),
    Column("tag_id", String(36), ForeignKey("tags.id")),
)


class Note(Base):
    __tablename__ = "notes"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    memo_date: Mapped[str] = mapped_column(String(8), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    tags = relationship(
        "Tag",
        secondary=note_tag_association,
        back_populates="notes",
        lazy="selectin",
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    notes = relationship(
        "Note",
        secondary=note_tag_association,
        back_populates="tags",
        lazy="selectin",
    )
