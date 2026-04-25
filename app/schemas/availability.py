from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class AvailabilitySlotCreateRequest(BaseModel):
    dentist_name: str = Field(min_length=3, max_length=120)
    start_time: datetime
    end_time: datetime
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_time_range(self) -> "AvailabilitySlotCreateRequest":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class AvailabilitySlotUpdateRequest(BaseModel):
    dentist_name: str | None = Field(default=None, min_length=3, max_length=120)
    start_time: datetime | None = None
    end_time: datetime | None = None
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_payload(self) -> "AvailabilitySlotUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        if self.start_time is not None and self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class AvailabilitySlotRead(BaseModel):
    id: int
    dentist_name: str
    start_time: datetime
    end_time: datetime
    is_reserved: bool
    notes: str | None
    created_at: datetime


class AvailabilitySlotActionResponse(BaseModel):
    message: str
    slot: AvailabilitySlotRead
