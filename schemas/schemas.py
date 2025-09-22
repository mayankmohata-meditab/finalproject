from pydantic import BaseModel

class Place(BaseModel):
    id:str
    loc: str
    status: str
    description: str | None = None
    price: int
    userId: str
    latitude:float
    longitude:float

    class Config:
        form_attributes = True
