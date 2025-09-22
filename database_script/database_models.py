from sqlalchemy.orm import declarative_base
from sqlalchemy import Column,Integer,Numeric,Boolean,String,DateTime,Float


Base=declarative_base()

class Places(Base):
    __tablename__="TABLE_ONE"
    id=Column(String,primary_key=True,index=True)
    loc=Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    status=Column(String)
    description=Column(String)
    price=Column(Float)
    userId=Column(String)
