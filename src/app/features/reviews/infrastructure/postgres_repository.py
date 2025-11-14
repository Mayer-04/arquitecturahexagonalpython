from collections.abc import Callable, Sequence
from typing import TypeVar
from uuid import UUID

from sqlalchemy import (
    delete,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.features.reviews.domain.entities.review import Review
from app.features.reviews.domain.entities.review_comment import ReviewComment
from app.features.reviews.domain.entities.review_image import ReviewImage
from app.features.reviews.domain.entities.review_vote import ReviewVote
from app.features.reviews.domain.exceptions import (
    ReviewAlreadyExistsError,
    ReviewNotFoundError,
)
from app.features.reviews.domain.repositories import ReviewRepository
from app.features.reviews.infrastructure.mappers import (
    map_comment,
    map_image,
    map_review,
    map_vote,
)
from app.features.reviews.infrastructure.tables import (
    review_comments_table,
    review_images_table,
    review_votes_table,
    reviews_table,
)

T = TypeVar("T")


class PostgresReviewRepository(ReviewRepository):
    """Repositorio concreto para Postgres usando SQLAlchemy Core."""

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

            return map_review(row)

        return self._run_in_transaction(_operation)

    def get_review(self, review_id: UUID) -> Review | None:
        row = (
            self._session.execute(select(reviews_table).where(reviews_table.c.id == review_id))
            .mappings()
            .first()
        )
        return map_review(row) if row else None

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

        return [map_review(row) for row in rows]

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

            return map_review(row)

        return self._run_in_transaction(_operation)

    def delete_review(self, review_id: UUID) -> None:
        def _operation(session: Session) -> None:
            result = session.execute(
                delete(reviews_table)
                .where(reviews_table.c.id == review_id)
                .returning(reviews_table.c.id)
            )

            deleted_id = result.scalar_one_or_none()

            if deleted_id is None:
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
            return map_image(row)

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
        return [map_image(row) for row in rows]

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
            return map_comment(row)

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
        return [map_comment(row) for row in rows]

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
            return map_vote(row)

        return self._run_in_transaction(_operation)

    def get_votes_summary(self, review_id: UUID) -> tuple[int, int]:
        useful, not_useful = self._session.execute(
            select(
                func.count().filter(review_votes_table.c.useful.is_(True)),
                func.count().filter(review_votes_table.c.useful.is_(False)),
            ).where(review_votes_table.c.review_id == review_id)
        ).one()

        return int(useful or 0), int(not_useful or 0)

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
