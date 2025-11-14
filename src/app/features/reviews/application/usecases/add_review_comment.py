from uuid import UUID

from app.features.reviews.application.dtos.review_comment_dto import ReviewCommentDTO
from app.features.reviews.application.mappers import to_review_comment_dto
from app.features.reviews.domain.entities.review_comment import ReviewComment
from app.features.reviews.domain.exceptions import ReviewNotFoundError
from app.features.reviews.domain.repositories import ReviewRepository


class AddReviewCommentUseCase:
    def __init__(
        self,
        repository: ReviewRepository,
    ) -> None:
        self._repository = repository

    def execute(self, review_id: UUID, user_id: UUID, comment_text: str) -> ReviewCommentDTO:
        if self._repository.get_review(review_id) is None:
            raise ReviewNotFoundError(f"Review {review_id} was not found")
        comment = ReviewComment(review_id=review_id, user_id=user_id, comment_text=comment_text)
        created = self._repository.add_comment(comment)
        dto = to_review_comment_dto(created)

        return dto
