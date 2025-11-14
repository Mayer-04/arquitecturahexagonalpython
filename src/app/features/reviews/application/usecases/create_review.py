from app.features.reviews.application.dtos.create_review_dto import CreateReviewDTO
from app.features.reviews.application.dtos.review_dto import ReviewDTO
from app.features.reviews.application.mappers import to_review_dto
from app.features.reviews.domain.entities.review import Review
from app.features.reviews.domain.entities.review_image import ReviewImage
from app.features.reviews.domain.repositories import ReviewRepository


class CreateReviewUseCase:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self, dto: CreateReviewDTO) -> ReviewDTO:
        review = Review(
            record_id=dto.record_id,
            user_id=dto.user_id,
            rent_amount=dto.rent_amount,
            review_text=dto.review_text,
            rating=dto.rating,
        )
        created = self._repository.create_review(review)

        for image_url in dto.image_urls:
            self._repository.add_image(ReviewImage(review_id=created.id, image_url=image_url))

        return to_review_dto(created)
