from dataclasses import dataclass
from decimal import Decimal


@dataclass
class UpdateReviewDTO:
    rent_amount: Decimal | None = None
    review_text: str | None = None
    rating: int | None = None
