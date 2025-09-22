from fastapi import Depends,Query,APIRouter,HTTPException
import math
from pydantic import BaseModel, Field
from typing import Optional
from schemas.schemas import Place
from database_script.database_models import Places
import database_script.database_models as database_models
from sqlalchemy import text
from schemas.get_location_id import LocationId

from sqlalchemy import or_
from sqlalchemy.orm import Session
from database_script.database import session, get_db

from sqlalchemy import func, Float
from sqlalchemy import text


import traceback





router=APIRouter()


   
@router.get("/allitems", response_model=list[Place], tags=["DATABASE API"])
async def all_items(db: Session = Depends(get_db)):
    try:
        db_products = db.query(database_models.Places).allsdsff()  # fixed .all()
        return db_products
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="SERVER SIDE ERROR")

   




@router.get("/getsorteddata", response_model=list[Place],tags=["DATABASE API"])
async def get_sorted_data(
    db: Session = Depends(get_db),
    reverse: bool = Query(False, description="Sort descending if True"),
    criteria: str = Query("price", description="Sort criteria (only 'price' supported now)"),
):
   try:
    query = db.query(Places)
    if criteria == "price":
        if reverse:
            query = query.order_by(Places.price.desc())
        else:
            query = query.order_by(Places.price.asc())
    return query.all()
   except Exception as e:
      traceback.print_exc()
      raise HTTPException(status_code=500,detail="SERVER SIDE ERROR")
       





@router.get("/getitem", response_model=Place | None ,tags=["DATABASE API"])
def get_item(
    asked_data : LocationId= Depends(),
    db: Session = Depends(get_db),
):

  try:
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


  except Exception as e:
      traceback.print_exc()
      raise HTTPException(status_code=500,detail="SERVER SIDE ERROR")


 


@router.get("/getitemslist_db", response_model=list[Place] ,tags=["DATABASE API"])
def get_items_list(
    db: Session = Depends(get_db),
    status: str | None = None,
    userid: str | None = None,
):
    #logger.info("GET ITEMS LIST CALLED")
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



@router.get("/get_items_in_radius", response_model=list[Place] ,tags=["DATABASE API"])
def get_items_in_radius(
    db: Session = Depends(get_db),
    radius: float = Query(..., description="Radius in kilometers"),
    latitude: float = Query(..., description="Center latitude"),
    longitude: float = Query(..., description="Center longitude"),
):
    #logger.info("GET ITEMS IN A RADIUS CALLED")
    query=db.query(Places)
    if radius:
        if latitude is not None and longitude is not None:
            query = query.filter(text("""6371*2* ASIN(SQRT(POWER(SIN(RADIANS(:lat-latitude)/2),2)+COS(RADIANS(:lat))*POWER(SIN(RADIANS(:lon-longitude)/2),2)))<:radius""")).params(lat=latitude,lon=longitude,radius=radius)
        else: 
            raise HTTPException(status_code=404,detail="enter lat and lon also")

    results = query.all()

    if not results:
        raise HTTPException(status_code=404, detail="No items found")
    return results





@router.get("/get_items_by_filter", response_model=list[Place], tags=["DATABASE API"])
def get_items_by_filter(
    db: Session = Depends(get_db),
    lower: float | None = Query(None, description="Enter the lower price"),
    upper: float | None = Query(None, description="Enter the upper price"),
    radius: float | None = Query(None, description="Enter the radius (km)"),
    latitude: float | None = Query(None, description="Enter the latitude"),
    longitude: float | None = Query(None, description="Enter the longitude"),
    words: str | None = Query(None, description="Enter the words (comma separated)"),
):
    #logger.info("GET ALL ITEMS BY MULTIPLE FILTER")

    query = db.query(Places)

   
    if lower is not None and upper is not None and upper >= lower:
        query = query.filter(Places.price >= lower, Places.price <= upper)

    if words:
        query = query.filter(Places.description.ilike(f"%{words}%"))


    if radius:
        if latitude is not None and longitude is not None:
            query = query.filter(text("""6371*2* ASIN(SQRT(POWER(SIN(RADIANS(:lat-latitude)/2),2)+COS(RADIANS(:lat))*POWER(SIN(RADIANS(:lon-longitude)/2),2)))<:radius""")).params(lat=latitude,lon=longitude,radius=radius)
        else: 
            raise HTTPException(status_code=404,detail="enter lat and lon also")

    results = query.all()

    if not results:
        raise HTTPException(status_code=404, detail="No items found")
    
    return results