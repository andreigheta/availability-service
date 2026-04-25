from datetime import datetime

import httpx

from app.core.config import settings
from app.schemas.availability import (
    AvailabilitySlotCreateRequest,
    AvailabilitySlotRead,
    AvailabilitySlotUpdateRequest,
)


class DatabaseServiceError(Exception):
    pass


class DatabaseServiceValidationError(DatabaseServiceError):
    pass


class DatabaseServiceConflictError(DatabaseServiceError):
    pass


class DatabaseServiceNotFoundError(DatabaseServiceError):
    pass


class DatabaseServiceClient:
    def __init__(self) -> None:
        self.base_url = settings.database_service_url.rstrip("/")
        self.timeout = settings.request_timeout_seconds

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
    ) -> httpx.Response:
        url = f"{self.base_url}{path}"
        try:
            response = httpx.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise DatabaseServiceError("database-service is unreachable") from exc

        if response.status_code >= 500:
            raise DatabaseServiceError("database-service returned a server error")

        return response

    def list_available_slots(
        self,
        *,
        dentist_name: str | None,
        start_from: datetime | None,
        start_to: datetime | None,
        limit: int,
        offset: int,
    ) -> list[AvailabilitySlotRead]:
        params = {
            "is_reserved": "false",
            "limit": limit,
            "offset": offset,
        }
        if dentist_name is not None:
            params["dentist_name"] = dentist_name
        if start_from is not None:
            params["start_from"] = start_from.isoformat()
        if start_to is not None:
            params["start_to"] = start_to.isoformat()

        response = self._request("GET", "/slots", params=params)
        if response.status_code == 400:
            raise DatabaseServiceValidationError("invalid slot search criteria")

        response.raise_for_status()
        return [AvailabilitySlotRead.model_validate(item) for item in response.json()]

    def create_slot(self, payload: AvailabilitySlotCreateRequest) -> AvailabilitySlotRead:
        response = self._request("POST", "/slots", json=payload.model_dump(mode="json"))
        if response.status_code == 400:
            raise DatabaseServiceValidationError("invalid slot data")
        if response.status_code == 409:
            raise DatabaseServiceConflictError("slot overlaps an existing slot")

        response.raise_for_status()
        return AvailabilitySlotRead.model_validate(response.json())

    def update_slot(self, slot_id: int, payload: AvailabilitySlotUpdateRequest) -> AvailabilitySlotRead:
        response = self._request(
            "PATCH",
            f"/slots/{slot_id}",
            json=payload.model_dump(exclude_unset=True, mode="json"),
        )
        if response.status_code == 400:
            raise DatabaseServiceValidationError("invalid slot data")
        if response.status_code == 404:
            raise DatabaseServiceNotFoundError("slot not found")
        if response.status_code == 409:
            raise DatabaseServiceConflictError("slot cannot be updated")

        response.raise_for_status()
        return AvailabilitySlotRead.model_validate(response.json())

    def delete_slot(self, slot_id: int) -> None:
        response = self._request("DELETE", f"/slots/{slot_id}")
        if response.status_code == 404:
            raise DatabaseServiceNotFoundError("slot not found")
        if response.status_code == 409:
            raise DatabaseServiceConflictError("slot cannot be deleted")

        response.raise_for_status()
