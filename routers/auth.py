from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from models import User, BlacklistedToken
from schemas import UserCreate, Token, UserCreateResponse
from auth import hash_password, verify_password, create_access_token, decode_access_token, oauth2_scheme
import os 
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  

router = APIRouter(prefix="/auth")

ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY") 


@router.post("/user_register", response_model=UserCreateResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if user.role == "admin":
        if not user.admin_key or user.admin_key != ADMIN_SECRET_KEY:
            raise HTTPException(status_code=403, detail="Invalid admin key")


    password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=password, role=user.role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})

    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    token_data = decode_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    expires_at = datetime.fromtimestamp(token_data["exp"])
    blacklisted_token = BlacklistedToken(token=token, expires_at=expires_at)

    db.add(blacklisted_token)
    db.commit()
    return {"message": "Logged out successfully"}
