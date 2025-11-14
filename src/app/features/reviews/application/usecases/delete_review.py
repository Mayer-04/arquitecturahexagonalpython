from uuid import UUID

from app.features.reviews.domain.exceptions import ReviewNotFoundError
from app.features.reviews.domain.repositories import ReviewRepository


class DeleteReviewUseCase:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self, review_id: UUID) -> None:
        review = self._repository.get_review(review_id)
        if review is None:
            raise ReviewNotFoundError(f"Review {review_id} was not found")
        self._repository.delete_review(review_id)
