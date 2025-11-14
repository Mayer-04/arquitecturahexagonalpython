from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True, frozen=True)
class ReviewDTO:
    """Representación de salida para exponer reseñas fuera del dominio."""

    id: UUID
    record_id: UUID
    user_id: UUID
    rent_amount: Decimal | None
    review_text: str
    rating: int
    created_at: datetime
