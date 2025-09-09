from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import create_engine

db_url="sqlite:///DataBase.db"


engine=create_engine(db_url)


session=sessionmaker(autoflush=False,autocommit=False,bind=engine)


Base=declarative_base()



def get_db():
    db=session()
    try:
      yield db
    finally:
      db.close()