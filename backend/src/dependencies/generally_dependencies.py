from fastapi import Query

from src.models.generally_models import PaginationParamsModel


def get_pagination_params(
    page: int = Query(1, ge=1, description='Page number, starting from 1'),
    per_page: int = Query(10, ge=2, le=100, description='Items per page (2-100)'),
) -> PaginationParamsModel:
    """Dependencies for getting pagination parameters."""
    return PaginationParamsModel(page=page, per_page=per_page)
