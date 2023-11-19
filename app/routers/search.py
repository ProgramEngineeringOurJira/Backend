from typing import List
from uuid import UUID

from beanie.operators import RegEx
from fastapi import APIRouter, Depends, Path, status

from app.auth.oauth2 import member
from app.schemas.documents import Issue, UserAssignedWorkplace

router = APIRouter(tags=["Search"])


@router.post(
    "/{workplace_id}/search/users/{searching_string}",
    response_model=List[UserAssignedWorkplace],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def search_users(
    workplace_id: UUID = Path(...), searching_string: str = Path(...), user: UserAssignedWorkplace = Depends(member)
):
    users = await UserAssignedWorkplace.find(
        UserAssignedWorkplace.workplace.id == workplace_id,
        RegEx(UserAssignedWorkplace.user.name, f"^{searching_string}"),
        fetch_links=True,
    ).to_list()
    return users


@router.post(
    "/{workplace_id}/search/issues/{searching_string}",
    response_model=List[Issue],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def search_issues(
    workplace_id: UUID = Path(...), searching_string: str = Path(...), user: UserAssignedWorkplace = Depends(member)
):
    issues = await Issue.find(
        Issue.workplace.id == workplace_id, RegEx(Issue.name, f"^{searching_string}"), fetch_links=True
    ).to_list()
    return issues


@router.get(
    "/{workplace_id}/search/user/issues",
    response_model=List[Issue],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def search_issues_for_user(workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(member)):
    issues = await Issue.find(Issue.workplace.id == workplace_id, fetch_links=True).to_list()
    user_issues = [i for i in issues if user in i.implementers]
    return user_issues
