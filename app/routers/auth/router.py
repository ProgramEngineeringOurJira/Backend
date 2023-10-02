from fastapi import APIRouter, Body, Depends, Request, status
from fastapi.responses import RedirectResponse

from app.auth.hash import get_password_hash, verify_password
from app.auth.jwt_token import create_access_token, create_refresh_token
from app.auth.oauth2 import get_current_user
from app.core.exceptions import UserFoundException, TimeOutCodeException, IncorrectCodeException
from app.email.email import Email
from app.core.redis_session import Redis

from .schemas import SuccessfulResponse, Token, TokenData, User, UserRegister

from uuid import uuid4

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user_auth: UserRegister = Body(...)):
    """Authenticates and returns the user's JWT"""
    user = await User.by_email(user_auth.email)
    if not user:
        raise UserFoundException("Юзера нет")
    if not verify_password(user_auth.password, user.password):
        return UserFoundException("не правильный логин или пароль")
    access_token = create_access_token(TokenData(email=user.email))
    refresh_token = create_refresh_token(TokenData(email=user.email))
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh/", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(user: User = Depends(get_current_user)):
    access_token = create_access_token(TokenData(email=user.email))
    refresh_token = create_refresh_token(TokenData(email=user.email))

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_register: UserRegister, request: Request):
    redis= Redis()
    user = await User.by_email(user_register.email)
    if user is not None:
        raise UserFoundException("Юзер уже существует")
    # TODO отправка на почту
    uuid = str(uuid4())
    url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/verifyemail/{uuid}"
    await redis.set_uuid_email(uuid, "1234")
    await Email(url, [user_register.email]).sendMail()
    return SuccessfulResponse()


@router.get("/verifyemail/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str, redis: Redis = Depends(Redis), user_register: UserRegister = Body()):
    check = await redis.get_uuid(user=[user_register.email, user_register.password])
    if check is None:
        raise TimeOutCodeException(error="Время истекло")
    if check != token:
        raise IncorrectCodeException(error="Код не верен")
    
    hashed = get_password_hash(user_register.password)
    user = User(email=user_register.email, password=hashed)
    await user.create()
    
    return RedirectResponse("/")  


@router.get("/profile/", response_model=User, status_code=status.HTTP_200_OK)
async def get_user_profile(user: User = Depends(get_current_user)):
    return user
