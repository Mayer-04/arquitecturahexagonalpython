from uuid import UUID

from app.features.reviews.application.dtos.review_dto import ReviewDTO
from app.features.reviews.application.mappers import to_review_dto
from app.features.reviews.domain.repositories import ReviewRepository


class ListReviewsForRecordUseCase:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self, record_id: UUID, *, limit: int = 20, offset: int = 0) -> list[ReviewDTO]:
        reviews = self._repository.list_reviews_for_record(record_id, limit=limit, offset=offset)
        return [to_review_dto(review) for review in reviews]
