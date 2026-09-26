"""
Router: /api/v1/categories
CRUD endpoints for Product Categories.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud.category as cat_crud
from database.session import get_db
from schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CategoryWithProductCount,
)

router = APIRouter(prefix="/categories", tags=["Product Categories"])


@router.get(
    "/",
    response_model=list[CategoryWithProductCount],
    summary="List all Product Categories",
)
def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[CategoryWithProductCount]:
    categories = cat_crud.get_categories(db, skip=skip, limit=limit)
    return [
        CategoryWithProductCount(
            **CategoryResponse.model_validate(cat).model_dump(),
            product_count=cat_crud.count_products_in_category(db, cat.id),
        )
        for cat in categories
    ]


@router.get(
    "/{category_id}",
    response_model=CategoryWithProductCount,
    summary="Get a single Category",
)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryWithProductCount:
    cat = cat_crud.get_category(db, category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return CategoryWithProductCount(
        **CategoryResponse.model_validate(cat).model_dump(),
        product_count=cat_crud.count_products_in_category(db, cat.id),
    )


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Product Category",
)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)) -> CategoryResponse:
    existing = cat_crud.get_category_by_name(db, data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{data.name}' already exists",
        )
    return cat_crud.create_category(db, data)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update a Category",
)
def update_category(
    category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)
) -> CategoryResponse:
    cat = cat_crud.update_category(db, category_id, data)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return cat


@router.delete(
    "/{category_id}",
    summary="Delete a Category (safe — refuses if active products exist)",
)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> dict:
    success, message = cat_crud.delete_category(db, category_id)
    if not success:
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in message
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(status_code=code, detail=message)
    return {"detail": message}
