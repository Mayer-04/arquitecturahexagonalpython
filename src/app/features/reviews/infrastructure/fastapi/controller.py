from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.features.reviews.application.dtos.create_review_dto import CreateReviewDTO
from app.features.reviews.application.dtos.update_review_dto import UpdateReviewDTO
from app.features.reviews.application.usecases.add_review_comment import (
    AddReviewCommentUseCase,
)
from app.features.reviews.application.usecases.add_review_image import (
    AddReviewImageUseCase,
)
from app.features.reviews.application.usecases.cast_review_vote import (
    CastReviewVoteUseCase,
)
from app.features.reviews.application.usecases.create_review import CreateReviewUseCase
from app.features.reviews.application.usecases.delete_review import DeleteReviewUseCase
from app.features.reviews.application.usecases.get_review import GetReviewUseCase
from app.features.reviews.application.usecases.get_review_vote_summary import (
    GetReviewVoteSummaryUseCase,
)
from app.features.reviews.application.usecases.list_review_comments import (
    ListReviewCommentsUseCase,
)
from app.features.reviews.application.usecases.list_review_images import (
    ListReviewImagesUseCase,
)
from app.features.reviews.application.usecases.list_reviews_for_record import (
    ListReviewsForRecordUseCase,
)
from app.features.reviews.application.usecases.update_review import UpdateReviewUseCase
from app.features.reviews.domain.exceptions import (
    InvalidReviewRatingError,
    ReviewAlreadyExistsError,
    ReviewNotFoundError,
)
from app.features.reviews.domain.repositories import ReviewRepository
from app.features.reviews.infrastructure.postgres_repository import (
    PostgresReviewRepository,
)
from app.shared.infrastructure.database import get_db

DbSession = Annotated[Session, Depends(get_db)]


def get_review_repository(db: DbSession) -> ReviewRepository:
    return PostgresReviewRepository(db)


RepositoryDep = Annotated[ReviewRepository, Depends(get_review_repository)]


class ReviewResponse(BaseModel):
    id: UUID
    record_id: UUID
    user_id: UUID
    rent_amount: Decimal | None
    review_text: str
    rating: int
    created_at: datetime


class ReviewImageResponse(BaseModel):
    id: UUID
    review_id: UUID
    image_url: str
    uploaded_at: datetime


class ReviewCommentResponse(BaseModel):
    id: UUID
    review_id: UUID
    user_id: UUID
    comment_text: str
    created_at: datetime


class ReviewVoteResponse(BaseModel):
    id: UUID
    review_id: UUID
    user_id: UUID
    useful: bool
    created_at: datetime


class VoteSummaryResponse(BaseModel):
    review_id: UUID
    useful_votes: int
    not_useful_votes: int


class CreateReviewPayload(BaseModel):
    record_id: UUID
    user_id: UUID
    rent_amount: Decimal | None = None
    review_text: str = Field(min_length=1, max_length=10_000)
    rating: int = Field(ge=1, le=5)
    image_urls: list[str] = Field(default_factory=list)


class UpdateReviewPayload(BaseModel):
    rent_amount: Decimal | None = None
    review_text: str | None = Field(default=None, min_length=1, max_length=10_000)
    rating: int | None = Field(default=None, ge=1, le=5)


class CommentPayload(BaseModel):
    user_id: UUID
    comment_text: str = Field(min_length=1, max_length=2000)


class ImagePayload(BaseModel):
    image_url: str = Field(min_length=1)


class VotePayload(BaseModel):
    user_id: UUID
    useful: bool


def create_review(
    payload: CreateReviewPayload,
    repository: RepositoryDep,
) -> ReviewResponse:
    usecase = CreateReviewUseCase(repository)
    try:
        dto = usecase.execute(
            CreateReviewDTO(
                record_id=payload.record_id,
                user_id=payload.user_id,
                rent_amount=payload.rent_amount,
                review_text=payload.review_text,
                rating=payload.rating,
                image_urls=payload.image_urls,
            )
        )
    except ReviewAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidReviewRatingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return ReviewResponse.model_validate(asdict(dto))


def get_review(review_id: UUID, repository: RepositoryDep) -> ReviewResponse:
    usecase = GetReviewUseCase(repository)
    try:
        dto = usecase.execute(review_id)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ReviewResponse.model_validate(asdict(dto))


def list_reviews_for_record(
    record_id: UUID,
    repository: RepositoryDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Sequence[ReviewResponse]:
    usecase = ListReviewsForRecordUseCase(repository)
    dtos = usecase.execute(record_id, limit=limit, offset=offset)
    return [ReviewResponse.model_validate(asdict(dto)) for dto in dtos]


def update_review(
    review_id: UUID,
    payload: UpdateReviewPayload,
    repository: RepositoryDep,
) -> ReviewResponse:
    usecase = UpdateReviewUseCase(repository)
    try:
        dto = usecase.execute(
            review_id,
            UpdateReviewDTO(
                rent_amount=payload.rent_amount,
                review_text=payload.review_text,
                rating=payload.rating,
            ),
        )
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidReviewRatingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return ReviewResponse.model_validate(asdict(dto))


def delete_review(review_id: UUID, repository: RepositoryDep) -> None:
    usecase = DeleteReviewUseCase(repository)
    try:
        usecase.execute(review_id)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def add_image(
    review_id: UUID, payload: ImagePayload, repository: RepositoryDep
) -> ReviewImageResponse:
    usecase = AddReviewImageUseCase(repository)
    try:
        dto = usecase.execute(review_id, payload.image_url)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ReviewImageResponse.model_validate(asdict(dto))


def list_images(review_id: UUID, repository: RepositoryDep) -> Sequence[ReviewImageResponse]:
    usecase = ListReviewImagesUseCase(repository)
    try:
        dtos = usecase.execute(review_id)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [ReviewImageResponse.model_validate(asdict(dto)) for dto in dtos]


def add_comment(
    review_id: UUID,
    payload: CommentPayload,
    repository: RepositoryDep,
) -> ReviewCommentResponse:
    usecase = AddReviewCommentUseCase(repository)
    try:
        dto = usecase.execute(review_id, payload.user_id, payload.comment_text)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ReviewCommentResponse.model_validate(asdict(dto))


def list_comments(
    review_id: UUID,
    repository: RepositoryDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Sequence[ReviewCommentResponse]:
    usecase = ListReviewCommentsUseCase(repository)
    try:
        dtos = usecase.execute(review_id, limit=limit, offset=offset)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [ReviewCommentResponse.model_validate(asdict(dto)) for dto in dtos]


def cast_vote(
    review_id: UUID,
    payload: VotePayload,
    repository: RepositoryDep,
) -> ReviewVoteResponse:
    usecase = CastReviewVoteUseCase(repository)
    try:
        dto = usecase.execute(review_id, payload.user_id, payload.useful)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ReviewVoteResponse.model_validate(asdict(dto))


def vote_summary(review_id: UUID, repository: RepositoryDep) -> VoteSummaryResponse:
    usecase = GetReviewVoteSummaryUseCase(repository)
    try:
        dto = usecase.execute(review_id)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return VoteSummaryResponse.model_validate(asdict(dto))
