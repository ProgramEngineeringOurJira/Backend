from fastapi import APIRouter, Depends, status

from app.auth.hash import get_password_hash, verify_password
from app.auth.jwt_token import create_access_token, create_refresh_token
from app.auth.oauth2 import get_current_user
from app.core.exceptions import Unauthorized, UserFoundException

from .schemas import SuccessfulResponse, Token, TokenData, User, UserRegister

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user_auth: UserRegister):
    """Authenticates and returns the user's JWT"""
    user = await User.by_email(user_auth.email)
    if not verify_password(user_auth.password, user.password):
        return Unauthorized
    access_token = create_access_token(TokenData(email=user.email))
    refresh_token = create_refresh_token(TokenData(email=user.email))
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh/", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(user: User = Depends(get_current_user)):
    access_token = create_access_token(TokenData(email=user.email))
    refresh_token = create_refresh_token(TokenData(email=user.email))

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_register: UserRegister):
    user = await User.by_email(user_register.email)
    if user is not None:
        raise UserFoundException()
    # TODO отправка на почту
    hashed = get_password_hash(user_register.password)
    user = User(email=user_register.email, password=hashed)
    await user.create()
    return SuccessfulResponse()


@router.get("/profile/", response_model=User, status_code=status.HTTP_201_CREATED)
async def get_user_profile(user: User = Depends(get_current_user)):
    return user
