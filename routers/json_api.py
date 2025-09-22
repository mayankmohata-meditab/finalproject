from fastapi import FastAPI,Query,APIRouter
from fastapi.encoders import jsonable_encoder
import json
import math
import numpy as np
from pydantic import Field
from typing import List,Optional,Union,Annotated,Dict
json_router_ =APIRouter()
places=""

def load_data():
  with open("placeslist.json","r") as f:
     datas=json.load(f)
  return datas


@json_router_.get("/all_items",tags=["JSON API"])
def get_all_places():
    datas=load_data()
    return datas

@json_router_.get("/sort_items/",tags=["JSON API"])
def GetSortedData(criteria:str =Query("price",regex="^(price|id)$",description="Field to sort by"), reverse:str=Query("false",regex="^(true|false)$",description="Enter order by which you want to sort")):
    datas=load_data()
    sorted_items=sorted(datas,key=lambda x: x[criteria],reverse=(reverse=="false"))
    return{"criteria":criteria,"reverse":reverse,"items":sorted_items}

@json_router_.get("/getitems",tags=["JSON API"])
def get_items(
    id_: Optional[str] = Query(None, description="Enter the id"),
    location: Optional[str] = Query(None, description="Enter the lat and long in 'lat,lon' format")
):
    datas=load_data()
    if id_ is None and location is None:
        return {"data": "Field empty"}

    if id_ is not None:
        for a in datas:
            if a["id"] == id_:
                return a
        return {"data": "ID not found"}

    if location is not None:
        try:
            lat, lon = map(str.strip, location.split(","))
        except ValueError:
            return {"error": "Invalid location format. Use 'lat,lon'"}

        for place in datas:
            if place["loc"][0] == float(lat) and place["loc"][1] == float(lon):
                return place
        return {"data": "Location not found"}

        

@json_router_.get("/getitemslist", tags=["JSON API"])
def getitemslist(
    userId: Annotated[Optional[str], Query( description="Enter userId")]=None,
    status: Annotated[Optional[str], Query( description="Enter status")]=None
):

    datas = load_data()
    l = datas

    if userId is not None:
        print("entered..................")
        l = [item for item in l if item["userId"] == userId]
        print(l)
    if status is not None:
        l = [item for item in l if item["status"] == status]
    if l:
        return {"data": l}
    else:
        return {"error":[]}






@json_router_.get("/get_items_by_radius",tags=["JSON API"])
def get_items_by_radius(
    radius: Optional[int] = Query(None, description="Enter the radius in km"),
    lat: str = Query(..., description="Enter latitude of base location"),
    lon: str = Query(..., description="Enter longitude of the base location")
):
    datas=load_data()
    if radius is None:
        return {"error": "Please enter radius"}

    lat = float(lat.strip())
    lon = float(lon.strip())
    R = 6371  

    array_of_locations = np.radians(np.array([p["loc"] for p in datas]))
    lats = array_of_locations[:, 0]
    lons = array_of_locations[:, 1]

    lat0 = np.radians(lat)
    lon0 = np.radians(lon)

    dphi = lats - lat0
    dlambda = lons - lon0

    # Haversine formula
    a = np.sin(dphi/2)**2 + np.cos(lat0) * np.cos(lats) * np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distances = R * c

    result = [dist for place, dist in zip(datas, distances) if dist <= radius]

    return {"results": result}

@json_router_.get("/get_items_by_filter",tags=["JSON API"],operation_id="getitemsbyfilter")
def get_items_by_filter(
    filterby: List[str] = Query(..., description="Enter the criteria (price, desc, radius)"),
    radius: Optional[int] = Query(None, description="Enter Radius (km)"),
    lower: Optional[int] = Query(None, description="Enter lower price"),
    upper: Optional[int] = Query(None, description="Enter upper price"),
    lat: Optional[str] = Query(None, description="Enter the latitude"),
    lon: Optional[str] = Query(None, description="Enter the longitude"),
    words: Optional[List[str]] = Query(None, description="Enter the words for description")
):
    datas=load_data()
    filtered_places = datas.copy()

    for criteria in filterby:

        if criteria == "price":
            if lower is None or upper is None:
                return {"error": "Please provide both lower and upper price limits"}
            filtered_places = [
                place for place in filtered_places 
                if lower <= place["price"] <= upper
            ]

        elif criteria == "desc":
            if not words:
                return {"error": "Please provide words to search in description"}
            ans = []
            for place in filtered_places:
                for word in words:
                    if word.lower() in place["description"].lower() if place["description"]!= None else "":
                        ans.append(place)
                        break  
            filtered_places = ans

        elif criteria == "radius":
            if radius is None or lat is None or lon is None:
                return {"error": "Please provide radius, latitude, and longitude"}

            lat = float(lat.strip())
            lon = float(lon.strip())
            R = 6371  

            array_of_locations = np.radians(np.array([p["loc"] for p in filtered_places]))
            lats = array_of_locations[:, 0]
            lons = array_of_locations[:, 1]

            lat0 = np.radians(lat)
            lon0 = np.radians(lon)

            dphi = lats - lat0
            dlambda = lons - lon0

            # Haversine formula
            a = np.sin(dphi/2)**2 + np.cos(lat0) * np.cos(lats) * np.sin(dlambda/2)**2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            distances = R * c

            filtered_places = [
                {**place, "distance_km": float(dist)}
                for place, dist in zip(filtered_places, distances)
                if dist <= radius
            ]

        else:
            return {"error": f"Invalid criteria: {criteria}"}

    return {"results": filtered_places}