import json
import pathlib

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request, status
from fastapi.responses import FileResponse, RedirectResponse

from app.auth.hash import get_password_hash, verify_password
from app.auth.jwt_token import create_access_token, create_refresh_token
from app.auth.oauth2 import get_current_user
from app.config import client_api_settings
from app.core.avatar import Avatar
from app.core.email import Email
from app.core.exceptions import AvatarNotFoundException, EmailVerificationException, UserFoundException
from app.core.redis_session import Redis
from app.schemas.documents import User
from app.schemas.models import SuccessfulResponse
from app.schemas.models.auth import Token, TokenData, UserLogin, UserRegister

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user_auth: UserLogin = Body(...)):
    """Authenticates and returns the user's JWT"""
    user = await User.by_email(user_auth.email)
    if not user:
        raise UserFoundException("Юзера нет")
    if not verify_password(user_auth.password, user.password):
        raise UserFoundException("не правильный логин или пароль")
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
    background_tasks.add_task(email.send_registration_mail, request, redis, user_register)
    return SuccessfulResponse()


@router.get("/verifyemail/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str, redis: Redis = Depends(Redis)):
    check = await redis.get_user(uuid=token)
    if check is None:
        raise EmailVerificationException("Произошла ошибка! Истекло время или неправильный код")

    user_data = json.loads(check)
    hashed = get_password_hash(user_data["password"])

    user = User(email=user_data["email"], password=hashed, name=user_data["name"])
    await Avatar.generate_avatar(str(user.id))

    await user.create()

    return RedirectResponse(client_api_settings.MAIN_URL)


@router.get("/profile/", response_model=User, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_user_profile(user: User = Depends(get_current_user)):
    return user


@router.get("/profile/avatar", response_class=FileResponse, status_code=status.HTTP_200_OK)
async def get_user_avatar(user: User = Depends(get_current_user)):
    storage = pathlib.Path(__file__).parent.parent.parent.resolve()
    avatar_folder = storage.joinpath(pathlib.Path("assets/avatars"))
    avatar_path = avatar_folder.joinpath(pathlib.Path(str(user.id) + ".png"))

    if not pathlib.Path.is_file(avatar_path):
        raise AvatarNotFoundException("Аватарка не найдена")

    return FileResponse(avatar_path)
