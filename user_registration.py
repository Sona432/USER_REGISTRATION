from fastapi import FastAPI, HTTPException, Depends, Form
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List

# Define your database connection URL here
DATABASE_URL = "postgresql://postgres:Opensona@123@localhost:5432/template1"

# Create a SQLAlchemy database engine
engine = create_engine(DATABASE_URL)

# Create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a FastAPI app
app = FastAPI()

# Create a SQLAlchemy base model
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(int)

# Define the Profile model
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    profile_picture = Column(String)

Base.metadata.create_all(bind=engine)

# Pydantic model for user registration
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    phone: int

# Pydantic model for user details
class UserDetail(BaseModel):
    full_name: str
    email: str
    phone: int
    profile_picture: str

# User registration route
@app.post("/register/", response_model=UserDetail)
def register_user(user: UserCreate):
    db = SessionLocal()
    # Check if the email or phone already exists
    existing_user = db.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_phone = db.query(User).filter_by(phone=user.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # Create a new user
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return UserDetail(**db_user.__dict__)

# Get user details by user_id
@app.get("/user/{user_id}", response_model=UserDetail)
def get_user_details(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(Profile).filter_by(user_id=user_id).first()
    if profile is None:
        profile_picture = ""
    else:
        profile_picture = profile.profile_picture

    db.close()
    return UserDetail(
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        profile_picture=profile_picture,
    )