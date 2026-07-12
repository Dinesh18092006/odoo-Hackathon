"""Common schema components reused across modules."""
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TimestampSchema(BaseModel):
    """Mixin for models with created_at/updated_at."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
