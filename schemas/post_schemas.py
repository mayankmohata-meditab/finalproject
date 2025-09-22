from pydantic import BaseModel,Field,computed_field
from typing import List,Optional,Union,Annotated,Dict

class PostItem(BaseModel):
    id: Annotated[str,Field(...,description="Enter Id")]
    status: Annotated[str,Field(...,description="Enter Status")]
    description: Annotated[str,Field(...,description="Enter description")]
    price: Annotated[float,Field(...,description="Enter Price")]
    userId: Annotated[str,Field(...,description="Enter userId")]
    latitude:Annotated[float,Field(...,description="Enter latitude")]
    longitude:Annotated[float,Field(...,description="Enter longitude")]

    @computed_field
    @property
    def loc(self)->str:
       return  str([self.latitude,self.longitude])