from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.availability import (
    AvailabilitySlotActionResponse,
    AvailabilitySlotCreateRequest,
    AvailabilitySlotRead,
    AvailabilitySlotUpdateRequest,
)
from app.services.database_client import (
    DatabaseServiceClient,
    DatabaseServiceConflictError,
    DatabaseServiceError,
    DatabaseServiceNotFoundError,
    DatabaseServiceValidationError,
)

router = APIRouter()
db_client = DatabaseServiceClient()

PaginationLimit = Annotated[int, Query(ge=1, le=500)]
PaginationOffset = Annotated[int, Query(ge=0)]


@router.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/availability/slots", response_model=list[AvailabilitySlotRead], tags=["availability"])
def list_available_slots(
    dentist_name: str | None = None,
    start_from: datetime | None = None,
    start_to: datetime | None = None,
    limit: PaginationLimit = 100,
    offset: PaginationOffset = 0,
) -> list[AvailabilitySlotRead]:
    if start_from is not None and start_to is not None and start_to < start_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_to must be later than or equal to start_from",
        )

    try:
        return db_client.list_available_slots(
            dentist_name=dentist_name,
            start_from=start_from,
            start_to=start_to,
            limit=limit,
            offset=offset,
        )
    except DatabaseServiceValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DatabaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post(
    "/availability/slots",
    response_model=AvailabilitySlotActionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["availability"],
)
def create_slot(payload: AvailabilitySlotCreateRequest) -> AvailabilitySlotActionResponse:
    try:
        slot = db_client.create_slot(payload)
        return AvailabilitySlotActionResponse(message="slot created successfully", slot=slot)
    except DatabaseServiceValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DatabaseServiceConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DatabaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.patch(
    "/availability/slots/{slot_id}",
    response_model=AvailabilitySlotActionResponse,
    tags=["availability"],
)
def update_slot(slot_id: int, payload: AvailabilitySlotUpdateRequest) -> AvailabilitySlotActionResponse:
    try:
        slot = db_client.update_slot(slot_id, payload)
        return AvailabilitySlotActionResponse(message="slot updated successfully", slot=slot)
    except DatabaseServiceValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DatabaseServiceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DatabaseServiceConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DatabaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.delete("/availability/slots/{slot_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["availability"])
def delete_slot(slot_id: int) -> None:
    try:
        db_client.delete_slot(slot_id)
    except DatabaseServiceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DatabaseServiceConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DatabaseServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
