from fastapi import APIRouter, status

from app.features.reviews.infrastructure.fastapi import controller

reviews_router = APIRouter(prefix="/reviews", tags=["reviews"])

reviews_router.post(
    "/", response_model=controller.ReviewResponse, status_code=status.HTTP_201_CREATED
)(controller.create_review)

reviews_router.get("/{review_id}", response_model=controller.ReviewResponse)(controller.get_review)

reviews_router.get("/record/{record_id}", response_model=list[controller.ReviewResponse])(
    controller.list_reviews_for_record
)

reviews_router.put("/{review_id}", response_model=controller.ReviewResponse)(
    controller.update_review
)
reviews_router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)(
    controller.delete_review
)

reviews_router.post(
    "/{review_id}/images",
    response_model=controller.ReviewImageResponse,
    status_code=status.HTTP_201_CREATED,
)(controller.add_image)
reviews_router.get("/{review_id}/images", response_model=list[controller.ReviewImageResponse])(
    controller.list_images
)

reviews_router.post(
    "/{review_id}/comments",
    response_model=controller.ReviewCommentResponse,
    status_code=status.HTTP_201_CREATED,
)(controller.add_comment)

reviews_router.get(
    "/{review_id}/comments",
    response_model=list[controller.ReviewCommentResponse],
)(controller.list_comments)

reviews_router.post(
    "/{review_id}/votes",
    response_model=controller.ReviewVoteResponse,
    status_code=status.HTTP_201_CREATED,
)(controller.cast_vote)
reviews_router.get("/{review_id}/votes/summary", response_model=controller.VoteSummaryResponse)(
    controller.vote_summary
)
