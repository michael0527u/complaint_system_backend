from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from models import User, UserLogin
from database import users_collection
import bcrypt
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        register_number: str = payload.get("sub")
        if register_number is None:
            raise credentials_exception

        user = users_collection.find_one({"register_number": register_number})
        if user is None:
            raise credentials_exception

        return {
            "register_number": user["register_number"],
            "name": user["name"]
        }
    except JWTError:
        raise credentials_exception

@router.post("/signup")
def signup(user: User):
    existing_user = users_collection.find_one({"register_number": user.register_number})

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())

    users_collection.insert_one({
        "name": user.name,
        "register_number": user.register_number,
        "password": hashed_password.decode(),
        "phone_number": user.phone_number
    })

    return {"message": "Signup successful"}

@router.post("/login")
def login(user: UserLogin):
    existing_user = users_collection.find_one({"register_number": user.register_number})

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt.checkpw(user.password.encode(), existing_user["password"].encode()):
        raise HTTPException(status_code=400, detail="Incorrect password")

    token_data = {"sub": existing_user["register_number"]}

    access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "name": existing_user["name"],
            "register_number": existing_user["register_number"]
        }
    }
