from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(slots=True, kw_only=True)
class ReviewImage:
    review_id: UUID
    image_url: str

    id: UUID = field(default_factory=uuid4)
    uploaded_at: datetime = field(default_factory=datetime.now)
