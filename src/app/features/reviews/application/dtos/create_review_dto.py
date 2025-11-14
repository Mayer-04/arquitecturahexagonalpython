from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID


@dataclass
class CreateReviewDTO:
    record_id: UUID
    user_id: UUID
    rent_amount: Decimal | None
    review_text: str
    rating: int
    image_urls: list[str] = field(default_factory=list)
