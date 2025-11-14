from abc import ABC, abstractmethod
from uuid import UUID

from app.features.reviews.domain.entities.review import Review


class ReviewRepository(ABC):
    @abstractmethod
    def save(self, dto: Review) -> None:
        pass

    @abstractmethod
    def find_by_id(self, review_id: UUID) -> Review | None:
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> list[Review]:
        pass

    @abstractmethod
    def update(self, review_id: UUID, review: Review) -> Review | None:
        pass

    @abstractmethod
    def delete(self, review_id: UUID) -> bool:
        pass
