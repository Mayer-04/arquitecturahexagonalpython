from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class ReviewVoteSummaryDTO:
    review_id: UUID
    useful_votes: int
    not_useful_votes: int
