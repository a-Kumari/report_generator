import bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from dotenv import load_dotenv
import os
from database import get_db
from sqlalchemy.orm import Session
from models import User, BlacklistedToken
load_dotenv()  


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    data["exp"] = expire 
    return jwt.encode(data, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=os.getenv("ALGORITHM"))
    except JWTError:
        return None



def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> dict:
   
    blacklisted_token = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()

    if blacklisted_token:
        if blacklisted_token.is_expired():
            db.delete(blacklisted_token)
            db.commit()
        else:
            raise HTTPException(status_code=401, detail="Token has been blacklisted")
    
    user_data = decode_access_token(token)

    db_user = db.query(User).filter(User.email == user_data["sub"]).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database"
        )

    return {
        "sub": db_user.email,
        "role": db_user.role,
        "user_id": db_user.id
    }

