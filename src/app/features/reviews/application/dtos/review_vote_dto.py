from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True, frozen=True)
class ReviewVoteDTO:
    id: UUID
    review_id: UUID
    user_id: UUID
    useful: bool
    created_at: datetime
