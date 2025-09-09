import database_models
import database
from schemas import Place
import json


database_models.Base.metadata.create_all(bind=database.engine)


db=database.session()


with open("placeslist.json","r") as f:
   data=json.load(f)

for d in data:
   obj1=database_models.Places(id=d.get("id"),loc=str(d.get("loc")),status=d.get("status"), description=d.get("description"),price=d.get("price"), userId=d.get("userId"),latitude=d.get("loc")[0],longitude=d.get("loc")[1])
   db.add(obj1)
db.commit()
db.close()