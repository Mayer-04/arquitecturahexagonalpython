from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True, frozen=True)
class ReviewCommentDTO:
    id: UUID
    review_id: UUID
    user_id: UUID
    comment_text: str
    created_at: datetime
