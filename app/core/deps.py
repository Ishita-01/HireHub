from collections.abc import Generator
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.models import User, UserRole
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    # 1. Look for the cookie we set during login
    username = request.cookies.get("session_user")
    
    # 2. If no cookie, the user is not logged in
    if not username:
        return None
    
    # 3. Fetch the user from the DB based on the username
    user = db.query(User).filter(User.username == username).first()
    return user

async def auth_required(current_user: User = Depends(get_current_user)):
    # Helper to block access if not logged in
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login."
        )
    return current_user

def roleRequired(role:UserRole):
    def decorator(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return decorator
