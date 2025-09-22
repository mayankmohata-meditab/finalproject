import database_script.database_models as database_models
import database_script.database as database
from schemas.schemas import Place
import json
from logger_setup.all_logger import logger_db

def initialize():
  try: 
     database_models.Base.metadata.create_all(bind=database.engine)
     db=database.session()

     try: 
          with open("placeslist.json","r") as f:
             data=json.load(f)
             logger_db.info("Data File Found Successfully")
     except FileNotFoundError:
             print("SUCH FILE DOESN'T EXIST")
             logger_db.debug("NO SUCH FILE EXIST")

     for d in data:
         obj1=database_models.Places(id=d.get("id"),loc=str(d.get("loc")),status=d.get("status"), description=d.get("description"),price=d.get("price"), userId=d.get("userId"),latitude=d.get("loc")[0],longitude=d.get("loc")[1])
         db.add(obj1)
     db.commit()
     db.close()
     logger_db.info("DATABASE CREATED")



  except Exception as excp:
      print(type(excp))
      logger_db.critical("DATABASE NOT CREATED")




if __name__=="__main__":
   initialize()