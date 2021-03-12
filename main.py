from typing import Optional
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from pydantic.main import BaseModel

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
  username: str
  email: Optional[str] = None
  full_name: Optional[str] = None
  disabled: Optional[bool] = None

def fake_decode_token(token):
  return User(
    username=token + "fakedecoded", email="email@example.com", full_name="John Doe"
  )

async def get_current_user(token: str = Depends(oauth2_scheme)):
  user = fake_decode_token(token)
  return user

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
  return current_user

@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
  return {"token": token}