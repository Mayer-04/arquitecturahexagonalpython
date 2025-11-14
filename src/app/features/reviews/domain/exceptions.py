class ReviewError(Exception):
    """Base para errores del dominio de reseñas."""


class ReviewAlreadyExistsError(ReviewError):
    """Se lanzó al intentar registrar una reseña duplicada para el mismo usuario y vivienda."""


class ReviewNotFoundError(ReviewError):
    """La reseña solicitada no existe."""


class InvalidReviewRatingError(ReviewError):
    """La calificación enviada no respeta el rango permitido."""


class ReviewVoteError(ReviewError):
    """Error relacionado con los votos de la reseña."""
