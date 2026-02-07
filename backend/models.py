from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, JSON
from .database import Base
import enum

class Role(str, enum.Enum):
    MITARBEITER = "Mitarbeiter"
    MANAGER = "Manager"
    GESCHAEFTSFUEHRER = "Geschäftsführer"
    PENDING = "Pending"

# Deprecated Enum for Department, keeping for reference but now using table
# class Department(str, enum.Enum): ... 

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="Pending")
    department = Column(String) # For simplicity, keeping as String for now, could be ForeignKey later
    inventory = Column(JSON, default={})
