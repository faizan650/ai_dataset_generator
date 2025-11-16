from pydantic import BaseModel, constr

class UserSignup(BaseModel):
    username: str
    email: str
    password: constr(min_length=6, max_length=72)  # bcrypt-safe limit

class UserLogin(BaseModel):
    email: str
    password: constr(min_length=1, max_length=72)
