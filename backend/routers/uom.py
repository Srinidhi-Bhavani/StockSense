"""
Router: /api/v1/uom
CRUD endpoints for Units of Measure.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud.uom as uom_crud
from database.session import get_db
from schemas.uom import UOMCreate, UOMResponse, UOMUpdate

router = APIRouter(prefix="/uom", tags=["Units of Measure"])


@router.get("/", response_model=list[UOMResponse], summary="List all Units of Measure")
def list_uoms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[UOMResponse]:
    return uom_crud.get_uoms(db, skip=skip, limit=limit)


@router.get("/{uom_id}", response_model=UOMResponse, summary="Get a single UOM")
def get_uom(uom_id: int, db: Session = Depends(get_db)) -> UOMResponse:
    uom = uom_crud.get_uom(db, uom_id)
    if not uom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UOM not found")
    return uom


@router.post(
    "/",
    response_model=UOMResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Unit of Measure",
)
def create_uom(data: UOMCreate, db: Session = Depends(get_db)) -> UOMResponse:
    existing = uom_crud.get_uom_by_name(db, data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"UOM '{data.name}' already exists",
        )
    return uom_crud.create_uom(db, data)


@router.put("/{uom_id}", response_model=UOMResponse, summary="Update a UOM")
def update_uom(
    uom_id: int, data: UOMUpdate, db: Session = Depends(get_db)
) -> UOMResponse:
    uom = uom_crud.update_uom(db, uom_id, data)
    if not uom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UOM not found")
    return uom


@router.delete("/{uom_id}", summary="Delete a UOM (safe — refuses if products use it)")
def delete_uom(uom_id: int, db: Session = Depends(get_db)) -> dict:
    success, message = uom_crud.delete_uom(db, uom_id)
    if not success:
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in message
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(status_code=code, detail=message)
    return {"detail": message}
