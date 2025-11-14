from uuid import UUID

from app.features.reviews.application.dtos.review_dto import ReviewDTO
from app.features.reviews.application.dtos.update_review_dto import UpdateReviewDTO
from app.features.reviews.application.mappers import to_review_dto
from app.features.reviews.domain.exceptions import ReviewNotFoundError
from app.features.reviews.domain.repositories import ReviewRepository


class UpdateReviewUseCase:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self, review_id: UUID, dto: UpdateReviewDTO) -> ReviewDTO:
        review = self._repository.get_review(review_id)
        if review is None:
            raise ReviewNotFoundError(f"Review {review_id} was not found")

        if dto.rent_amount is not None:
            review.rent_amount = dto.rent_amount
        if dto.review_text is not None:
            review.review_text = dto.review_text
        if dto.rating is not None:
            review.rating = dto.rating

        updated = self._repository.update_review(review)
        return to_review_dto(updated)
