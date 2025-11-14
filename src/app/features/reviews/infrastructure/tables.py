# app/features/reviews/infrastructure/db/tables.py
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    MetaData,
    Numeric,
    SmallInteger,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID

metadata = MetaData()

reviews_table = Table(
    "reviews",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column("record_id", PGUUID(as_uuid=True), ForeignKey("records.id", ondelete="CASCADE")),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")),
    Column("rent_amount", Numeric(10, 2)),
    Column("review_text", Text, nullable=False),
    Column("rating", SmallInteger, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

review_images_table = Table(
    "review_images",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column("review_id", PGUUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE")),
    Column("image_url", Text, nullable=False),
    Column("uploaded_at", DateTime, nullable=False),
)

review_comments_table = Table(
    "review_comments",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column("review_id", PGUUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE")),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")),
    Column("comment_text", Text, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

review_votes_table = Table(
    "review_votes",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column("review_id", PGUUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE")),
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")),
    Column("useful", Boolean, nullable=False),
    Column("created_at", DateTime, nullable=False),
)
