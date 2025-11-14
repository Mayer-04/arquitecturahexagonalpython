from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True, frozen=True)
class ReviewImageDTO:
    id: UUID
    review_id: UUID
    image_url: str
    uploaded_at: datetime
