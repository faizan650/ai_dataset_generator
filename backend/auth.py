from fastapi import APIRouter, HTTPException
from database import users_collection
from models import UserSignup, UserLogin
from passlib.context import CryptContext

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# Bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    if isinstance(password, str):
        password = password.encode("utf-8")
    return pwd_context.hash(password[:72])


def verify_password(plain: str, hashed: str):
    if isinstance(plain, str):
        plain = plain.encode("utf-8")
    try:
        return pwd_context.verify(plain[:72], hashed)
    except ValueError:
        return False


# --------------------------
# ⭐ IMPORTANT: ADD OPTIONS ⭐
# --------------------------

@router.options("/signup")
async def signup_options():
    return {"message": "OK"}

@router.options("/login")
async def login_options():
    return {"message": "OK"}


# --------------------------
# SIGNUP
# --------------------------
@router.post("/signup")
def signup(user: UserSignup):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered.")

    hashed_pw = hash_password(user.password)
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_pw
    })
    return {"message": "User registered successfully"}


# --------------------------
# LOGIN
# --------------------------
@router.post("/login")
def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    return {
        "message": "Login successful",
        "username": db_user["username"],
        "email": db_user["email"]
    }
