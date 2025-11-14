from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.features.reviews.domain.exceptions import InvalidReviewRatingError


@dataclass(slots=True, kw_only=True)
class Review:
    record_id: UUID
    user_id: UUID
    rating: int

    rent_amount: Decimal | None
    review_text: str

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not 1 <= self.rating <= 5:
            raise InvalidReviewRatingError("Rating must be between 1 and 5")
