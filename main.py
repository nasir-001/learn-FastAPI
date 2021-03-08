from datetime import date, datetime, time, timedelta
from uuid import UUID
from fastapi import Cookie, FastAPI, Query
from enum import Enum
from typing import Dict, List, Set, Optional
from fastapi.param_functions import Body, Path

from pydantic import BaseModel, HttpUrl, EmailStr

class ModelName(str, Enum):
  alexnet = "alexnet"
  resnet = "resnet"
  lenet = "lenet"

class Image(BaseModel):
  url: HttpUrl
  name: str

class Item(BaseModel):
  name: str
  description: Optional[str] = None
  price: float
  tax: float = 10.5
  tags: List[str] = []
  image: Optional[List[Image]] = None

class User(BaseModel):
  username: str
  full_name: Optional[str] = None

class Offer(BaseModel):
  name: str
  description: Optional[str] = None
  price: float
  items: List[Item]

class UserIn(BaseModel):
  username: str
  password: str
  email: EmailStr
  full_name: Optional[str] = None

class UserOut(BaseModel):
  username: str
  email: EmailStr
  full_name: Optional[str] = None

app = FastAPI()

items = {
  "foo": {"name": "Foo", "price": 50.2},
  "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
  "baz": {
    "name": "Baz",
    "description": "There goes my baz",
    "price": 50.2,
    "tax": 10.5,
  },
}

@app.get('/')
async def read_root():
  return {"Hello": "World"}

@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
  return user

@app.post("/offers/")
async def create_offer(offer: Offer):
  return offer

@app.post("/index-weights/")
async def create_index_weight(weights: Dict[int, float]):
  return weights

@app.post("/images/multiple")
async def create_mutiple_images(images: List[Image]):
  return images

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
  return item

@app.get("/items/")
async def reat_items(ads_in: Optional[str] = Cookie(None)):
  return {"ads_in": ads_in}

@app.put("/items/{item_id}")
async def update_item(
  item_id: UUID,
  start_datetime: Optional[datetime] = Body(None),
  end_datetime: Optional[datetime] = Body(None),
  repeat_at: Optional[time] = Body(None),
  process_after: Optional[timedelta]= Body(None)
):

  start_process = start_datetime + process_after
  duration = end_datetime - start_process

  return {
    "Item_id": item_id,
    "start_datetime": start_datetime,
    "end_datetime": end_datetime,
    "repeat_at": repeat_at,
    "process_after": process_after,
    "start_process": start_process,
    "duration": duration
  }

@app.get('/users/me')
async def read_user_me():
  return {"user_id": "the current user"}

# path parameters

@app.get("/users/{user_id}")
async def read_user(user_id: str):
  return {"user_id": user_id}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
  if model_name == ModelName.alexnet:
    return {"model_name": model_name, "message": "Deep learning FTW!"}

  if model_name.value == "lenet":
    return {"model_name": model_name, "message": "LeCNN all the images"}

  return {"model_name": model_name, "message": "Have some residuals"}

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
  return {"file_path": file_path}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/{item_id}", response_model=Item, response_model_include=["name", "description"])
async def read_item(item_id: str):
  return items[item_id]

@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude=["tax"])
async def read_item_public_data(item_id: str):
  return items[item_id]

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
  user_id: int, item_id: str, q: Optional[str] = None, short: bool = False
):
  item = {"item_id": item_id, "owner_id": user_id}
  if q:
    item.update({"q": q})
  if not short:
    item.update(
      {
        "description": "This is an amazing item that has a long description"
      }
    )
  return item
