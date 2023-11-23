from typing import List
from uuid import UUID

from beanie.operators import RegEx, ElemMatch, In
from fastapi import APIRouter, Depends, Path, status

from app.auth.oauth2 import member
from app.schemas.documents import Issue, UserAssignedWorkplace

router = APIRouter(tags=["Search"])


# Поиск пользователей в данном воркплейсе по строке
@router.get(
    "/{workplace_id}/search/users",
    response_model=List[UserAssignedWorkplace],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def search_users(
    workplace_id: UUID = Path(...), searching_string: str | None = "", user: UserAssignedWorkplace = Depends(member)
):
    users = await UserAssignedWorkplace.find(
        UserAssignedWorkplace.workplace.id == workplace_id,
        RegEx(UserAssignedWorkplace.user.name, "^" + searching_string),
        fetch_links=True,
    ).to_list()
    return users


# Поиск задач в данном воркплейсе по строке
@router.get(
    "/{workplace_id}/search/issues",
    response_model=List[Issue],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def search_issues(
    workplace_id: UUID = Path(...), searching_string: str | None = "", user: UserAssignedWorkplace = Depends(member)
):
    issues = await Issue.find(
        Issue.workplace.id == workplace_id, RegEx(Issue.name, "^" + searching_string), fetch_links=True
    ).to_list()
    return issues


# Поиск всех задач, которые назначены пользователю в этом воркплейсе
@router.get(
    "/{workplace_id}/search/user/issues",
    response_model=List[Issue],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def search_issues_for_user(workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(member)):
    # Выдаёт пустой список (рекомендовал Артемий)
    # issues = await Issue.find(
    #     Issue.workplace.id == workplace_id,
    #     ElemMatch(Issue.implementers, {"id": user.id}),
    #     fetch_links=True
    # ).to_list()

    # Не работает и никогда не будет работать (это твой вариант)
    # issues = await Issue.find(
    #     Issue.workplace.id == workplace_id,
    #     In(Issue.implementers, [user]),
    #     fetch_links=True
    # ).to_list()

    # Мой рабочий вариант
    issues = await Issue.find(Issue.workplace.id == workplace_id, fetch_links=True).to_list()
    user_issues = [i for i in issues if user in i.implementers]
    return user_issues
