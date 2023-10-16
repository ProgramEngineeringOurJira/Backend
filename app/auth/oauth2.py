from typing import List
from uuid import UUID

from fastapi import Depends, Path
from fastapi.security import HTTPBearer

from app.auth.jwt_token import decode_token
from app.core.exceptions import ForbiddenException, Unauthorized, WorkplaceNotFoundError
from app.schemas.documents import Role, User, UserAssignedWorkplace

oauth2_scheme = HTTPBearer()


async def get_current_user(token: UUID = Depends(oauth2_scheme)) -> str:
    token = decode_token(token.credentials)
    user = await User.by_email(token.email)
    if not user:
        raise Unauthorized()
    return user


class RoleChecker:
    def __init__(self, role: List[Role]):
        self.role = role

    async def __call__(self, user: User = Depends(get_current_user), workplace_id: UUID = Path(...)) -> str:
        user_assigned = await UserAssignedWorkplace.find(
            UserAssignedWorkplace.user.id == user.id,
            UserAssignedWorkplace.workplace.id == workplace_id,
            fetch_links=True,
        ).first_or_none()
        if not user_assigned:
            raise WorkplaceNotFoundError("Worplace не найден")
        if user_assigned.role in self.role:
            return user_assigned
        raise ForbiddenException("Нет прав.")


# доступно только админу
admin: RoleChecker = RoleChecker([Role.ADMIN])
# доступно админам и членам
member: RoleChecker = RoleChecker([Role.MEMBER, Role.ADMIN])
# доступно админам, членам и гостям
guest: RoleChecker = RoleChecker([Role.GUEST, Role.MEMBER, Role.ADMIN])
