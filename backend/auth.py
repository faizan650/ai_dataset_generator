from fastapi import APIRouter, HTTPException
from database import users_collection
from models import UserSignup, UserLogin
from argon2 import PasswordHasher

router = APIRouter(prefix="/auth", tags=["Auth"])

# Use Argon2 instead of bcrypt
ph = PasswordHasher()


def hash_password(password: str):
    return ph.hash(password)


def verify_password(plain: str, hashed: str):
    try:
        return ph.verify(hashed, plain)
    except Exception:
        return False


# --------------------------
# OPTIONS (CORS preflight)
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
