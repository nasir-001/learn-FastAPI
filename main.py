from fastapi import FastAPI, Query
from enum import Enum
from typing import Dict, List, Set, Optional
from fastapi.param_functions import Body, Path

from pydantic import BaseModel, HttpUrl

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
  tax: Optional[float] = None
  tags: Set[str] = set()
  image: Optional[List[Image]] = None

class User(BaseModel):
  username: str
  full_name: Optional[str] = None

class Offer(BaseModel):
  name: str
  description: Optional[str] = None
  price: float
  items: List[Item]

app = FastAPI()

# first step

@app.get('/')
async def read_root():
  return {"Hello": "World"}

@app.post("/offers/")
async def create_offer(offer: Offer):
  return offer

@app.post("/index-weights/")
async def create_index_weight(weights: Dict[int, float]):
  return weights

@app.post("/images/multiple")
async def create_mutiple_images(images: List[Image]):
  return images

@app.post("/items/")
async def create_item(item: Item):
  item_dict = item.dict()
  if item.tax:
    price_with_tax = item.price + item.tax
    item_dict.update({"price_with_tax": price_with_tax})
  return item_dict

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
  results = {"item_id": item_id, "item": item}
  return results

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

# Query parameters

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/{item_id}")
async def read_item(
  *, 
  item_id: int = Path(..., title="The ID of the item to get", gt=0, le=100), 
  q: str,
  size: float = Query(..., gt=0, lt=10.5)
):
  results = {"items": item_id}
  if q:
    results.update({"q": q})
  return results

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
