from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse, FirebaseAuthRequest
from app.services.auth import register_user, authenticate_user, authenticate_firebase_user, get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register User")
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, user_in)

@router.post("/login", response_model=Token, summary="User Login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    access_token = authenticate_user(db, credentials)
    return Token(access_token=access_token, token_type="bearer")

@router.post("/firebase", response_model=Token, summary="Firebase Google Sign-In")
def firebase_login(req: FirebaseAuthRequest, db: Session = Depends(get_db)):
    access_token = authenticate_firebase_user(db, req.id_token)
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse, summary="Get Current Authenticated User")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
