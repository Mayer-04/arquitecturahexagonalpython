from uuid import UUID

from app.features.reviews.application.dtos.review_comment_dto import ReviewCommentDTO
from app.features.reviews.application.dtos.review_dto import ReviewDTO
from app.features.reviews.application.dtos.review_image_dto import ReviewImageDTO
from app.features.reviews.application.dtos.review_vote_dto import ReviewVoteDTO
from app.features.reviews.application.dtos.review_vote_summary_dto import ReviewVoteSummaryDTO
from app.features.reviews.domain.entities.review import Review
from app.features.reviews.domain.entities.review_comment import ReviewComment
from app.features.reviews.domain.entities.review_image import ReviewImage
from app.features.reviews.domain.entities.review_vote import ReviewVote


def to_review_dto(review: Review) -> ReviewDTO:
    return ReviewDTO(
        id=review.id,
        record_id=review.record_id,
        user_id=review.user_id,
        rent_amount=review.rent_amount,
        review_text=review.review_text,
        rating=review.rating,
        created_at=review.created_at,
    )


def to_review_image_dto(image: ReviewImage) -> ReviewImageDTO:
    return ReviewImageDTO(
        id=image.id,
        review_id=image.review_id,
        image_url=image.image_url,
        uploaded_at=image.uploaded_at,
    )


def to_review_comment_dto(comment: ReviewComment) -> ReviewCommentDTO:
    return ReviewCommentDTO(
        id=comment.id,
        review_id=comment.review_id,
        user_id=comment.user_id,
        comment_text=comment.comment_text,
        created_at=comment.created_at,
    )


def to_review_vote_dto(vote: ReviewVote) -> ReviewVoteDTO:
    return ReviewVoteDTO(
        id=vote.id,
        review_id=vote.review_id,
        user_id=vote.user_id,
        useful=vote.useful,
        created_at=vote.created_at,
    )


def to_vote_summary_dto(review_id: UUID, useful: int, not_useful: int) -> ReviewVoteSummaryDTO:
    return ReviewVoteSummaryDTO(
        review_id=review_id, useful_votes=useful, not_useful_votes=not_useful
    )
