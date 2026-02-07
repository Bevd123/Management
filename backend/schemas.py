from pydantic import BaseModel
from enum import Enum
from typing import Optional

class Role(str, Enum):
    MITARBEITER = "Mitarbeiter"
    MANAGER = "Manager"
    GESCHAEFTSFUEHRER = "Geschäftsführer"
    PENDING = "Pending"

# Department Schemas (Must be before User schemas if referenced, or independent)
class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserCreateAdmin(UserCreate):
    role: str
    department: str | None = None

class UserUpdateAdmin(BaseModel):
    role: str
    department: str | None = None
    username: str | None = None
    password: str | None = None

class User(UserBase):
    id: int
    role: str
    department: str | None
    inventory: dict = {}

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
