from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Optional
from fastapi import Query


class LocationId(BaseModel):
    id: Optional[str] = Query(None, description="Enter id")
    latitude: Optional[float] = Query(None, description="Enter latitude")
    longitude: Optional[float] = Query(None, description="Enter longitude")
