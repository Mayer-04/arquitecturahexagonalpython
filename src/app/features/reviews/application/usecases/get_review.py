from uuid import UUID

from app.features.reviews.application.dtos.review_dto import ReviewDTO
from app.features.reviews.application.mappers import to_review_dto
from app.features.reviews.domain.exceptions import ReviewNotFoundError
from app.features.reviews.domain.repositories import ReviewRepository


class GetReviewUseCase:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self, review_id: UUID) -> ReviewDTO:
        review = self._repository.get_review(review_id)
        if review is None:
            raise ReviewNotFoundError(f"Review {review_id} was not found")
        return to_review_dto(review)
