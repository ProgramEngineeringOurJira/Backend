from typing import List, Optional
from uuid import UUID

from beanie import DeleteRules, WriteRules
from beanie.operators import RegEx
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import admin, get_current_user, guest
from app.schemas.documents import Role, User, UserAssignedWorkplace, Workplace
from app.schemas.models import SuccessfulResponse, WorkplaceCreation

router = APIRouter(tags=["Workplace"])


@router.post("/workplace", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_workplace(workplace_creation: WorkplaceCreation = Body(...), user: User = Depends(get_current_user)):
    workplace = Workplace(**workplace_creation.model_dump())
    workplace.users = [UserAssignedWorkplace(user=user, workplace_id=workplace.id, role=Role.ADMIN)]
    await workplace.save(link_rule=WriteRules.WRITE)
    return SuccessfulResponse()


@router.get(
    "/workplaces/{workplace_id}",
    response_model=Workplace,
    status_code=status.HTTP_200_OK,
    response_model_exclude={"users"},
)
async def get_workplace(workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)):
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
    return workplace


@router.put("/workplaces/{workplace_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_workplace(
    workplace_creation: WorkplaceCreation = Body(...),
    workplace_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(admin),
):
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
    await workplace.update({"$set": workplace_creation.model_dump()})
    return SuccessfulResponse()


@router.delete("/workplaces/{workplace_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_workplace(workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(admin)):
    await UserAssignedWorkplace.find(UserAssignedWorkplace.workplace.id == workplace_id).delete()
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    await workplace.delete(link_rule=DeleteRules.DELETE_LINKS)
    return None

@router.get("/workplaces/{workplace_id}/users", response_model=List[UserAssignedWorkplace], status_code=status.HTTP_200_OK)
async def get_users(prefix_email: str | None = "", workplace_id: UUID = Path(), user: UserAssignedWorkplace = Depends(guest)):
    users = await UserAssignedWorkplace.find(UserAssignedWorkplace.workplace.id == workplace_id,
        RegEx(UserAssignedWorkplace.user.email, f"^{prefix_email}"),                  
        fetch_links=True).to_list()
    return users

# UserAssignedWorkplace.user.email[:len(prefix_email)] == prefix_email,