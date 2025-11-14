from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar
from uuid import UUID

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
    delete,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import RowMapping
from sqlalchemy.orm import Session

from app.features.reviews.domain.entities.review import Review
from app.features.reviews.domain.entities.review_comment import ReviewComment
from app.features.reviews.domain.entities.review_image import ReviewImage
from app.features.reviews.domain.entities.review_vote import ReviewVote
from app.features.reviews.domain.exceptions import ReviewAlreadyExistsError, ReviewNotFoundError
from app.features.reviews.domain.repositories import ReviewRepository

metadata = MetaData()

reviews_table = Table(
    "reviews",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column(
        "record_id",
        PGUUID(as_uuid=True),
        ForeignKey("records.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    ),
    Column("rent_amount", Numeric(10, 2)),
    Column("review_text", Text, nullable=False),
    Column("rating", SmallInteger, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

review_images_table = Table(
    "review_images",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column(
        "review_id",
        PGUUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("image_url", Text, nullable=False),
    Column("uploaded_at", DateTime, nullable=False),
)

review_comments_table = Table(
    "review_comments",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column(
        "review_id",
        PGUUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    ),
    Column("comment_text", Text, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

review_votes_table = Table(
    "review_votes",
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True),
    Column(
        "review_id",
        PGUUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    ),
    Column("useful", Boolean, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

T = TypeVar("T")


class PostgresReviewRepository(ReviewRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_review(self, review: Review) -> Review:
        def _operation(session: Session) -> Review:
            self._ensure_user_can_review(session, review.user_id, review.record_id)
            row = (
                session.execute(
                    insert(reviews_table)
                    .values(
                        {
                            "id": review.id,
                            "record_id": review.record_id,
                            "user_id": review.user_id,
                            "rent_amount": review.rent_amount,
                            "review_text": review.review_text,
                            "rating": review.rating,
                            "created_at": review.created_at,
                        }
                    )
                    .returning(reviews_table)
                )
                .mappings()
                .one()
            )
            return self._map_review(row)

        return self._run_in_transaction(_operation)

    def get_review(self, review_id: UUID) -> Review | None:
        row = (
            self._session.execute(select(reviews_table).where(reviews_table.c.id == review_id))
            .mappings()
            .first()
        )
        return self._map_review(row) if row else None

    def list_reviews_for_record(
        self, record_id: UUID, *, limit: int, offset: int
    ) -> Sequence[Review]:
        rows = (
            self._session.execute(
                select(reviews_table)
                .where(reviews_table.c.record_id == record_id)
                .order_by(reviews_table.c.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            .mappings()
            .all()
        )
        return [self._map_review(row) for row in rows]

    def update_review(self, review: Review) -> Review:
        def _operation(session: Session) -> Review:
            row = (
                session.execute(
                    update(reviews_table)
                    .where(reviews_table.c.id == review.id)
                    .values(
                        {
                            "rent_amount": review.rent_amount,
                            "review_text": review.review_text,
                            "rating": review.rating,
                        }
                    )
                    .returning(reviews_table)
                )
                .mappings()
                .first()
            )
            if row is None:
                raise ReviewNotFoundError(f"Review {review.id} was not found")
            return self._map_review(row)

        return self._run_in_transaction(_operation)

    def delete_review(self, review_id: UUID) -> None:
        def _operation(session: Session) -> None:
            result = session.execute(delete(reviews_table).where(reviews_table.c.id == review_id))
            if result.rowcount == 0:
                raise ReviewNotFoundError(f"Review {review_id} was not found")

        self._run_in_transaction(_operation)

    def add_image(self, image: ReviewImage) -> ReviewImage:
        def _operation(session: Session) -> ReviewImage:
            row = (
                session.execute(
                    insert(review_images_table)
                    .values(
                        {
                            "id": image.id,
                            "review_id": image.review_id,
                            "image_url": image.image_url,
                            "uploaded_at": image.uploaded_at,
                        }
                    )
                    .returning(review_images_table)
                )
                .mappings()
                .one()
            )
            return self._map_image(row)

        return self._run_in_transaction(_operation)

    def list_images(self, review_id: UUID) -> Sequence[ReviewImage]:
        rows = (
            self._session.execute(
                select(review_images_table)
                .where(review_images_table.c.review_id == review_id)
                .order_by(review_images_table.c.uploaded_at.desc())
            )
            .mappings()
            .all()
        )
        return [self._map_image(row) for row in rows]

    def add_comment(self, comment: ReviewComment) -> ReviewComment:
        def _operation(session: Session) -> ReviewComment:
            row = (
                session.execute(
                    insert(review_comments_table)
                    .values(
                        {
                            "id": comment.id,
                            "review_id": comment.review_id,
                            "user_id": comment.user_id,
                            "comment_text": comment.comment_text,
                            "created_at": comment.created_at,
                        }
                    )
                    .returning(review_comments_table)
                )
                .mappings()
                .one()
            )
            return self._map_comment(row)

        return self._run_in_transaction(_operation)

    def list_comments(self, review_id: UUID, *, limit: int, offset: int) -> Sequence[ReviewComment]:
        rows = (
            self._session.execute(
                select(review_comments_table)
                .where(review_comments_table.c.review_id == review_id)
                .order_by(review_comments_table.c.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            .mappings()
            .all()
        )
        return [self._map_comment(row) for row in rows]

    def upsert_vote(self, vote: ReviewVote) -> ReviewVote:
        def _operation(session: Session) -> ReviewVote:
            row = (
                session.execute(
                    pg_insert(review_votes_table)
                    .values(
                        {
                            "id": vote.id,
                            "review_id": vote.review_id,
                            "user_id": vote.user_id,
                            "useful": vote.useful,
                            "created_at": vote.created_at,
                        }
                    )
                    .on_conflict_do_update(
                        index_elements=[
                            review_votes_table.c.review_id,
                            review_votes_table.c.user_id,
                        ],
                        set_={"useful": vote.useful},
                    )
                    .returning(review_votes_table)
                )
                .mappings()
                .one()
            )
            return self._map_vote(row)

        return self._run_in_transaction(_operation)

    def get_votes_summary(self, review_id: UUID) -> tuple[int, int]:
        useful_votes, not_useful_votes = self._session.execute(
            select(
                func.count().filter(review_votes_table.c.useful.is_(True)),
                func.count().filter(review_votes_table.c.useful.is_(False)),
            ).where(review_votes_table.c.review_id == review_id)
        ).one()
        return int(useful_votes or 0), int(not_useful_votes or 0)

    def _ensure_user_can_review(self, session: Session, user_id: UUID, record_id: UUID) -> None:
        exists = session.execute(
            select(reviews_table.c.id).where(
                (reviews_table.c.user_id == user_id) & (reviews_table.c.record_id == record_id)
            )
        ).first()
        if exists:
            raise ReviewAlreadyExistsError("User already submitted a review for this record")

    def _run_in_transaction(self, operation: Callable[[Session], T]) -> T:
        with self._session.begin():
            return operation(self._session)

    @staticmethod
    def _map_review(row: RowMapping) -> Review:
        return Review(
            id=row["id"],
            record_id=row["record_id"],
            user_id=row["user_id"],
            rent_amount=row["rent_amount"],
            review_text=row["review_text"],
            rating=row["rating"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _map_image(row: RowMapping) -> ReviewImage:
        return ReviewImage(
            id=row["id"],
            review_id=row["review_id"],
            image_url=row["image_url"],
            uploaded_at=row["uploaded_at"],
        )

    @staticmethod
    def _map_comment(row: RowMapping) -> ReviewComment:
        return ReviewComment(
            id=row["id"],
            review_id=row["review_id"],
            user_id=row["user_id"],
            comment_text=row["comment_text"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _map_vote(row: RowMapping) -> ReviewVote:
        return ReviewVote(
            id=row["id"],
            review_id=row["review_id"],
            user_id=row["user_id"],
            useful=row["useful"],
            created_at=row["created_at"],
        )
