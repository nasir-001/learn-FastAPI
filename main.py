from fastapi import FastAPI
from enum import Enum

class ModelName(str, Enum):
  alexnet: "alexnet"
  resnet: "resnet"
  lenet: "lenet"

app = FastAPI()

@app.get('/')
async def read_root():
  return {"Hello": "World"}
