from uuid import UUID

from app.features.reviews.application.dtos.review_image_dto import ReviewImageDTO
from app.features.reviews.application.mappers import to_review_image_dto
from app.features.reviews.domain.entities.review_image import ReviewImage
from app.features.reviews.domain.exceptions import ReviewNotFoundError
from app.features.reviews.domain.repositories import ReviewRepository


class AddReviewImageUseCase:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self, review_id: UUID, image_url: str) -> ReviewImageDTO:
        if self._repository.get_review(review_id) is None:
            raise ReviewNotFoundError(f"Review {review_id} was not found")
        image = ReviewImage(review_id=review_id, image_url=image_url)
        created = self._repository.add_image(image)
        return to_review_image_dto(created)
