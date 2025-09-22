from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import create_engine

db_url="sqlite:///database_script/MeditabDatabase.db"

try: 
  engine=create_engine(db_url)
except Exception as ee:
  print(ee)


session=sessionmaker(autoflush=False,autocommit=False,bind=engine)


Base=declarative_base()



def get_db():
    db=session()
    try:
      yield db
    finally:
      db.close()