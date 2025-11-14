from uuid import UUID

from app.features.reviews.application.dtos.review_vote_dto import ReviewVoteDTO
from app.features.reviews.application.mappers import to_review_vote_dto
from app.features.reviews.domain.entities.review_vote import ReviewVote
from app.features.reviews.domain.exceptions import ReviewNotFoundError
from app.features.reviews.domain.repositories import ReviewRepository


class CastReviewVoteUseCase:
    def __init__(
        self,
        repository: ReviewRepository,
    ) -> None:
        self._repository = repository

    def execute(self, review_id: UUID, user_id: UUID, useful: bool) -> ReviewVoteDTO:
        if self._repository.get_review(review_id) is None:
            raise ReviewNotFoundError(f"Review {review_id} was not found")
        vote = ReviewVote(review_id=review_id, user_id=user_id, useful=useful)
        saved = self._repository.upsert_vote(vote)
        dto = to_review_vote_dto(saved)
        return dto
