from typing import Optional

import jwt  # type: ignore[import-error]
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel

# auth secrets
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# fake db
users_db = {
    "john_smith": {
        "username": "john_smith",
        "hashed_password": pwd_context.hash("john_smith"),
        "age": 25,
        "group": "users",
    },
    "admin1": {
        "username": "admin1",
        "hashed_password": pwd_context.hash("john_smith"),
        "age": 25,
        "group": "admin",
    },
}

app = FastAPI()


class User(BaseModel):
    username: str
    email: str
    age: int
    role: str


class TokenData(BaseModel):
    username: Optional[str] = None


class ModelInferenceOutput(BaseModel):
    result: float


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = users_db.get(token_data.username, None)  # type: ignore[arg-type]
    if user is None:
        raise credentials_exception
    return user


@app.get("/")
def index():
    return {"text": "ML model inference"}


@app.get("/analysis/{data}", response_model=ModelInferenceOutput)
def run_model_analysis(data: str, user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted.")
    result = sum(map(data.lower().count, "aeiuyo")) / len(data)
    return {"result": result}
