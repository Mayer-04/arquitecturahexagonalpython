from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(slots=True, kw_only=True)
class ReviewVote:
    review_id: UUID
    user_id: UUID
    useful: bool

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
