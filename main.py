from fastapi import FastAPI,Depends,Query
from sqlalchemy.orm import Session
# from .database import session, engine
from database import session,engine
from database_models import Places
import database_models
import json
from schemas import Place




app=FastAPI()
database_models.Base.metadata.create_all(bind=engine)
def db_init_():
   db=session()
   count=db.query(database_models.Places).count()
   if count==0:
     count=db.query
     filename="placeslist.json"
     with open(filename,"r") as f:
          data=json.load(f)

     for d in data:
      obj1=Places(id=d.get("id"),
      loc=str(d.get("loc")),
      status=d.get("status"),
      description=d.get("description"),
      price=d.get("price"),
      userId=d.get("userId"),lat=d.get("loc")[0],lon=d.get("loc")[1])
      db.add(obj1)
     db.commit()
     db.close()

def get_db():
    db=session()
    try:
      yield db
    finally:
      db.close()
db_init_()

@app.get("/allitems")
def all_items(db:Session=Depends(get_db), response_model=list[Place]):
   
   db_products=db.query(database_models.Places).all()
   return db_products


@app.get("/getsorteddata", response_model=list[Place])
def get_sorted_data(
    db: Session = Depends(get_db),
    reverse: bool = Query(False, description="Sort descending if True"),
    criteria: str = Query("price", description="Sort criteria (only 'price' supported now)"),
):
    query = db.query(Places)
    if criteria == "price":
        if reverse:
            query = query.order_by(Places.price.desc())
        else:
            query = query.order_by(Places.price.asc())
    return query.all()


@app.get("/getitem", response_model=Place | None)
def get_item(
    db: Session = Depends(get_db),
    id: str | None = None,
    location: str | None = None,
):
    if id:
        return db.query(Places).filter(Places.id == id).first()
    if location:
        return db.query(Places).filter(Places.loc == location).first()
    return None

@app.get("/getitemslist", response_model=list[Place])
def get_items_list(
    db: Session = Depends(get_db),
    status: str | None = None,
    userid: str | None = None,
):
    query = db.query(Places)
    if status:
        query = query.filter(Places.status == status)
    if userid:
        query = query.filter(Places.userId == userid)
    return query.all()


import math

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


from fastapi import Query

@app.get("/get_items_in_radius", response_model=list[Place])
def get_items_in_radius(
    db: Session = Depends(get_db),
    radius: float = Query(..., description="Radius in kilometers"),
    latitude: float = Query(..., description="Center latitude"),
    longitude: float = Query(..., description="Center longitude"),
):
    all_items = db.query(Places).all()
    result = []

    for item in all_items:
        if item.latitude is not None and item.longitude is not None:
            dist = haversine(latitude, longitude, item.latitude, item.longitude)
            if dist <= radius:
                result.append(item)

    return result


@app.get("/get_items_by_filter", response_model=list[Place])
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
