from fastapi import FastAPI,Depends,Query,APIRouter,HTTPException
import json
import math
from pydantic import BaseModel, Field
from typing import Optional,Annotated
from schemas import Place
from database_models import Places
import database_models


from sqlalchemy.orm import Session
from database import session, get_db


import logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)


formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(name)s::::%(message)s')

filehandler=logging.FileHandler("first.log")
filehandler.setFormatter(formatter)

logger.addHandler(filehandler)



router=APIRouter()

@router.get("/allitems", response_model=list[Place])
def all_items(db:Session=Depends(get_db)):
   
   db_products=db.query(database_models.Places).all()
   logger.info("GET ALL ITEMS ENDPOINT CALLED")
   return db_products



@router.get("/getsorteddata", response_model=list[Place])
def get_sorted_data(
    db: Session = Depends(get_db),
    reverse: bool = Query(False, description="Sort descending if True"),
    criteria: str = Query("price", description="Sort criteria (only 'price' supported now)"),
):
    logger.info("Get sorted Data CALLED")
    query = db.query(Places)
    if criteria == "price":
        if reverse:
            query = query.order_by(Places.price.desc())
        else:
            query = query.order_by(Places.price.asc())
    return query.all()


from fastapi import Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Annotated

class LocationId(BaseModel):
    id: Optional[str] = Query(None, description="Enter id")
    latitude: Optional[float] = Query(None, description="Enter latitude")
    longitude: Optional[float] = Query(None, description="Enter longitude")


@router.get("/getitem", response_model=Place | None)
def get_item(
    asked_data : LocationId= Depends(),
    db: Session = Depends(get_db),
):
    logger.info("GET A ITEM CALLED")


    if asked_data.id is not None:
        item = db.query(Places).filter(Places.id == asked_data.id).first()
        if not item:
            raise HTTPException(
                status_code=404, detail=f"Item with id {asked_data.id} not found"
            )
        return item

    lat = asked_data.latitude
    lon = asked_data.longitude

    
    if (lat is None) != (lon is None):
        raise HTTPException(
            status_code=400,
            detail="Both latitude and longitude must be provided"
        )

    if lat is not None and lon is not None:
        item = db.query(Places).filter(
            (Places.latitude == lat) & (Places.longitude == lon)
        ).first()
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Item with location ({lat}, {lon}) not found"
            )
        return item


    raise HTTPException(
        status_code=400,
        detail="Provide either id or (latitude + longitude)"
    )


 


@router.get("/getitemslist", response_model=list[Place])
def get_items_list(
    db: Session = Depends(get_db),
    status: str | None = None,
    userid: str | None = None,
):
    logger.info("GET ITEMS LIST CALLED")
    query = db.query(Places)
    if status:
        query = query.filter(Places.status == status)
    if userid:
        query = query.filter(Places.userId == userid)
    item = query.all()
    if not item:
        raise HTTPException(status_code=400,detail="No such items found")



def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c



@router.get("/get_items_in_radius", response_model=list[Place])
def get_items_in_radius(
    db: Session = Depends(get_db),
    radius: float = Query(..., description="Radius in kilometers"),
    latitude: float = Query(..., description="Center latitude"),
    longitude: float = Query(..., description="Center longitude"),
):
    logger.info("GET ITEMS IN A RADIUS CALLED")
    all_items = db.query(Places).all()
    result = []

    for item in all_items:
        if item.latitude is not None and item.longitude is not None:
            dist = haversine(latitude, longitude, item.latitude, item.longitude)
            if dist <= radius:
                result.append(item)

    return result



@router.get("/get_items_by_filter", response_model=list[Place])
def get_items_by_filter(
    db: Session = Depends(get_db),
    filterby: list[str] = Query(..., description="Enter the criteria (price, radius, desc)"),
    lower: float | None = None,
    upper: float | None = None,
    radius: float | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    words: str | None = None,
):
    logger.info("GET ALL ITEMS BY MULTIPLE FILTER")
    results = db.query(Places).all()

    if "price" in filterby and lower is not None and upper is not None:
        results = [item for item in results if lower <= item.price <= upper]

   
    if "radius" in filterby and radius and latitude and longitude:
        filtered = []
        for item in results:
            if item.latitude and item.longitude:
                dist = haversine(latitude, longitude, item.latitude, item.longitude)
                if dist <= radius:
                    filtered.append(item)
        results = filtered

   
    if "desc" in filterby and words:
        keywords = [w.strip().lower() for w in words.split(",")]
        results = [
            item for item in results
            if item.description and any(word in item.description.lower() for word in keywords)
        ]

    return results
