from uuid import UUID

from app.features.reviews.application.dtos.review_comment_dto import ReviewCommentDTO
from app.features.reviews.application.mappers import to_review_comment_dto
from app.features.reviews.domain.exceptions import ReviewNotFoundError
from app.features.reviews.domain.repositories import ReviewRepository


class ListReviewCommentsUseCase:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(
        self, review_id: UUID, *, limit: int = 20, offset: int = 0
    ) -> list[ReviewCommentDTO]:
        if self._repository.get_review(review_id) is None:
            raise ReviewNotFoundError(f"Review {review_id} was not found")
        comments = self._repository.list_comments(review_id, limit=limit, offset=offset)
        return [to_review_comment_dto(comment) for comment in comments]
