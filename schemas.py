from pydantic import BaseModel

class Place(BaseModel):
    id: str
    loc: str
    status: str
    description: str | None = None
    price: int
    userId: str

    class Config:
        form_attributes = True
