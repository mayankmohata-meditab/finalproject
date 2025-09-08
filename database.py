from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_url="sqlite:///DataBase.db"
engine=create_engine(db_url)
session=sessionmaker(autoflush=False,autocommit=False,bind=engine)