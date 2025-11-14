from uuid import UUID

from app.features.reviews.application.dtos.review_image_dto import ReviewImageDTO
from app.features.reviews.application.mappers import to_review_image_dto
from app.features.reviews.domain.exceptions import ReviewNotFoundError
from app.features.reviews.domain.repositories import ReviewRepository


class ListReviewImagesUseCase:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self, review_id: UUID) -> list[ReviewImageDTO]:
        if self._repository.get_review(review_id) is None:
            raise ReviewNotFoundError(f"Review {review_id} was not found")
        images = self._repository.list_images(review_id)
        return [to_review_image_dto(image) for image in images]
