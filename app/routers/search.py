from typing import List
from uuid import UUID

from beanie.operators import RegEx
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import member
from app.schemas.documents import Issue, UserAssignedWorkplace
from app.schemas.models.search import SearchModel

router = APIRouter(tags=["Search"])


@router.post(
    "/{workplace_id}/search/users",
    response_model=List[UserAssignedWorkplace],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def search_users(
    workplace_id: UUID = Path(...), start_str: SearchModel = Body(...), user: UserAssignedWorkplace = Depends(member)
):
    users = await UserAssignedWorkplace.find(
        UserAssignedWorkplace.workplace.id == workplace_id,
        RegEx(UserAssignedWorkplace.user.email, f"^{start_str.start_string}"),
        fetch_links=True,
    ).to_list()
    return users


@router.post(
    "/{workplace_id}/search/issues",
    response_model=List[Issue],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def search_issues(
    workplace_id: UUID = Path(...), start_str: SearchModel = Body(...), user: UserAssignedWorkplace = Depends(member)
):
    issues = await Issue.find(
        Issue.workplace.id == workplace_id, RegEx(Issue.name, f"^{start_str.start_string}"), fetch_links=True
    ).to_list()
    return issues
