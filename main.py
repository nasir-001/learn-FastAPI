from datetime import date, datetime, time, timedelta
from uuid import UUID
from fastapi import Cookie, FastAPI, Query, status, Form, File, UploadFile, HTTPException, Request
from enum import Enum
from typing import Dict, List, Set, Optional, Union
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Body, Path
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

from pydantic import BaseModel, HttpUrl, EmailStr
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

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
  # image: Optional[List[Image]] = None

class Items(BaseModel):
  title: str
  size: int

class User(BaseModel):
  username: str
  full_name: Optional[str] = None

class Offer(BaseModel):
  name: str
  description: Optional[str] = None
  price: float
  items: List[Item]

class UserBase(BaseModel):
  username: str
  email: EmailStr
  full_name: Optional[str] = None

class UserIn(UserBase):
  password: str
  
class UserOut(UserBase):
  pass

class UserInDB(UserBase):
  hashed_password: str

class BaseItem(BaseModel):
  description: str
  type: str

class CarItem(BaseItem):
  type = "car"

class PlaneItem(BaseItem):
  type = "plane"
  size: int

class Encode(BaseModel):
  title: str
  timestamp: datetime
  description: Optional[str] = None

class UnicornException(Exception):
  def __init__(self, name: str):
    self.name = name

items = {
  "foo": {"name": "Foo", "price": 50.2},
  "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
  "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

app = FastAPI()

@app.get("/keyword-weights/", response_model=Dict[str, float])
async def read_keyword_weights():
  return {"foo": 2.3, "bar": 3.4}

def fake_password_hasher(raw_password: str):
  return "secret" + raw_password

def fake_save_user(user_in: UserIn):
  hashed_password = fake_password_hasher(user_in.password)
  user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
  print("User saved! ..not really")
  return user_in_db

@app.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
  user_saved = fake_save_user(user_in)
  return user_saved

@app.post("/offers/")
async def create_offer(offer: Offer):
  return offer

@app.post("/index-weights/")
async def create_index_weight(weights: Dict[int, float]):
  return weights

@app.post("/images/multiple")
async def create_mutiple_images(images: List[Image]):
  return images

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
  return {"name": name}

@app.get("/items/")
async def reat_items(ads_in: Optional[str] = Cookie(None)):
  return {"ads_in": ads_in}

@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item):
  update_item_encoded = jsonable_encoder(item)
  items[item_id] = update_item_encoded
  return update_item_encoded

@app.patch("/items/{item_id}", response_model=Item)
async def update_with_patch(item_id: str, item: Item):
  stored_item_data = items[item_id]
  stored_item_model = Item(**stored_item_data)
  update_data = item.dict(exclude_unset=True)
  updated_item = stored_item_model.copy(update=update_data)
  items[item_id] = jsonable_encoder(updated_item)
  return updated_item


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


@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
  return {"username": username}

@app.post("/files/")
async def create_file(
  file: bytes = File(...), fileb: UploadFile = File(...), token: str = Form(...)
):
  return {
    "file_size": len(file),
    "file_content_type": fileb.content_type,
    "token": token,
    }

@app.post("/uploadfile/")
async def create_upload_file(file: List[UploadFile] = File(...)):
  return {"filename": file.filename}

@app.get("/")
async def main():
  content = """
    <body>
      <form action="/files/" enctype="multipart/form-data" method="post">
        <input name="files" type="file" multiple>
        <input type="submit">
      </form>
      <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
        <input name="files" type="file" multiple>
        <input type="submit">
      </form>
    </body>
  """
  return HTMLResponse(content=content)

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
  return JSONResponse(
    status_code=418,
    content={"message": f"Opps! {exc.name} did something. There goes a rainbow..."},
  )

@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
  if name == 'yolo':
    raise UnicornException(name=name)
  return {"unicorn_name": name}

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
  return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
  return JSONResponse(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
  )
  
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
  return items[item_id]

@app.post(
  "/itemss/", 
  tags=["testing"],
  response_description="The created item",
  deprecated=True 
)
async def creating(item: Items):
  """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
  return item

@app.put("/items/{id}")
def update_item(id: str, item: Encode):
  json_compatible_item_data = jsonable_encoder(item)
  