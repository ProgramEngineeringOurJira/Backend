import json
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request, status
from fastapi.responses import RedirectResponse

from app.auth.hash import get_password_hash, verify_password
from app.auth.jwt_token import create_access_token, create_refresh_token
from app.auth.oauth2 import get_current_user
from app.config import client_api_settings
from app.core import UserRegister
from app.core.email import Email
from app.core.exceptions import EmailVerificationException, UserFoundException
from app.core.redis_session import Redis
from app.schemas.auth import SuccessfulResponse, Token, TokenData, User

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
async def register_user(
    user_register: UserRegister,
    request: Request,
    background_tasks: BackgroundTasks,
    redis: Redis = Depends(Redis),
    email: Email = Depends(Email),
):
    user = await User.by_email(user_register.email)
    if user is not None:
        raise UserFoundException("Юзер уже существует")
    # Отправка на почту
    uuid = str(uuid4())
    url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/verifyemail/{uuid}"
    await redis.set_uuid_email(uuid, user_register)
    background_tasks.add_task(email.sendMail, url, user_register.email)

    return SuccessfulResponse(details=uuid)


@router.get("/verifyemail/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str, redis: Redis = Depends(Redis)):
    check = await redis.get_user(uuid=token)
    if check is None:
        raise EmailVerificationException("Произошла ошибка! Истекло время или неправильный код")

    user_data = json.loads(check)
    hashed = get_password_hash(user_data["password"])
    user = User(email=user_data["email"], password=hashed)
    await user.create()

    return RedirectResponse(client_api_settings.MAIN_URL)


@router.get("/profile/", response_model=User, status_code=status.HTTP_200_OK)
async def get_user_profile(user: User = Depends(get_current_user)):
    return user
