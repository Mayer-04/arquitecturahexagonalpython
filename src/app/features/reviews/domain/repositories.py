from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from app.features.reviews.domain.entities.review import Review
from app.features.reviews.domain.entities.review_comment import ReviewComment
from app.features.reviews.domain.entities.review_image import ReviewImage
from app.features.reviews.domain.entities.review_vote import ReviewVote


class ReviewRepository(Protocol):
    """Contrato para persistir y consultar reseñas y sus recursos relacionados."""

    def create_review(self, review: Review) -> Review: ...

    def get_review(self, review_id: UUID) -> Review | None: ...

    def list_reviews_for_record(
        self, record_id: UUID, *, limit: int, offset: int
    ) -> Sequence[Review]: ...

    def update_review(self, review: Review) -> Review: ...

    def delete_review(self, review_id: UUID) -> None: ...

    def add_image(self, image: ReviewImage) -> ReviewImage: ...

    def list_images(self, review_id: UUID) -> Sequence[ReviewImage]: ...

    def add_comment(self, comment: ReviewComment) -> ReviewComment: ...

    def list_comments(
        self, review_id: UUID, *, limit: int, offset: int
    ) -> Sequence[ReviewComment]: ...

    def upsert_vote(self, vote: ReviewVote) -> ReviewVote: ...

    def get_votes_summary(self, review_id: UUID) -> tuple[int, int]: ...
