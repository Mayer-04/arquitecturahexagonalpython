from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(slots=True, kw_only=True)
class ReviewComment:
    review_id: UUID
    user_id: UUID
    comment_text: str

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
