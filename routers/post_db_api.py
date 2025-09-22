from fastapi import APIRouter,Depends,Form
from schemas.post_schemas import PostItem
from sqlalchemy.orm import Session
from database_script.database import session, get_db
from database_script.database_models import Places

router_put_db=APIRouter()

@router_put_db.post("/putitems", tags=["DATABASE API"], response_model=PostItem)
def post_items(
    id: str = Form(...),
    status: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    userId: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    db: Session = Depends(get_db),
):
    item = PostItem(
        id=id,
        status=status,
        description=description,
        price=price,
        userId=userId,
        latitude=latitude,
        longitude=longitude,
    )
    obj1 = Places(**item.model_dump(mode="python"))
    db.add(obj1)
    db.commit()
    db.refresh(obj1)
    return item
