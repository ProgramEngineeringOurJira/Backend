from datetime import datetime, timedelta

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWEError
from pydantic import ValidationError

from app.config import client_api_settings
from app.core.exceptions import Unauthorized
from app.routers.auth.schemas import TokenData


def create_access_token(data: TokenData) -> str:
    expire = datetime.utcnow() + timedelta(seconds=client_api_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    data.exp = expire
    encoded_jwt = jwt.encode(
        dict(data),
        key=client_api_settings.AUTH_SECRET,
        algorithm=client_api_settings.AUTH_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(data: TokenData) -> str:
    expire = datetime.utcnow() + timedelta(seconds=client_api_settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    data.exp = expire
    encoded_jwt = jwt.encode(
        dict(data),
        key=client_api_settings.AUTH_SECRET,
        algorithm=client_api_settings.AUTH_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            key=client_api_settings.AUTH_SECRET,
            algorithms=[client_api_settings.AUTH_ALGORITHM],
        )
        if not payload:
            raise Unauthorized
        token_data = TokenData(**payload)
        if datetime.utcnow() > token_data.exp.utcnow():
            raise Unauthorized
    except (ExpiredSignatureError, JWEError, ValidationError) as e:
        raise Unauthorized from e
    return token_data
