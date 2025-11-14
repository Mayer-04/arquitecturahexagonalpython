from sqlalchemy.engine import RowMapping

from app.features.reviews.domain.entities.review import Review
from app.features.reviews.domain.entities.review_comment import ReviewComment
from app.features.reviews.domain.entities.review_image import ReviewImage
from app.features.reviews.domain.entities.review_vote import ReviewVote


def map_review(row: RowMapping) -> Review:
    return Review(
        id=row["id"],
        record_id=row["record_id"],
        user_id=row["user_id"],
        rent_amount=row["rent_amount"],
        review_text=row["review_text"],
        rating=row["rating"],
        created_at=row["created_at"],
    )


def map_image(row: RowMapping) -> ReviewImage:
    return ReviewImage(
        id=row["id"],
        review_id=row["review_id"],
        image_url=row["image_url"],
        uploaded_at=row["uploaded_at"],
    )


def map_comment(row: RowMapping) -> ReviewComment:
    return ReviewComment(
        id=row["id"],
        review_id=row["review_id"],
        user_id=row["user_id"],
        comment_text=row["comment_text"],
        created_at=row["created_at"],
    )


def map_vote(row: RowMapping) -> ReviewVote:
    return ReviewVote(
        id=row["id"],
        review_id=row["review_id"],
        user_id=row["user_id"],
        useful=row["useful"],
        created_at=row["created_at"],
    )
