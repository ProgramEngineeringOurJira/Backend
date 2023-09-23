from fastapi import Depends
from fastapi.security import HTTPBearer

from app.auth.jwt_token import decode_token
from app.core.exceptions import Unauthorized
from app.routers.auth.schemas import User

oauth2_scheme = HTTPBearer()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    token = decode_token(token.credentials)
    user = await User.by_email(token.email)
    if not user:
        raise Unauthorized
    return user
