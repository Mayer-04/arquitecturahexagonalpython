from uuid import UUID

from app.features.reviews.application.dtos.review_vote_summary_dto import ReviewVoteSummaryDTO
from app.features.reviews.application.mappers import to_vote_summary_dto
from app.features.reviews.domain.exceptions import ReviewNotFoundError
from app.features.reviews.domain.repositories import ReviewRepository


class GetReviewVoteSummaryUseCase:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self, review_id: UUID) -> ReviewVoteSummaryDTO:
        if self._repository.get_review(review_id) is None:
            raise ReviewNotFoundError(f"Review {review_id} was not found")
        useful, not_useful = self._repository.get_votes_summary(review_id)
        return to_vote_summary_dto(review_id, useful, not_useful)
