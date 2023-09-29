from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import admin, get_current_user, guest
from app.core.exceptions import WorkplaceNotFoundError
from app.routers.auth.schemas import Role, SuccessfulResponse, User, UserAssignedWorkplace

from .schemas import Workplace, WorkplaceCreation

router = APIRouter(tags=["Workplace"])


@router.post("/workplace", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_workplace(workplace_creation: WorkplaceCreation = Body(...), user: User = Depends(get_current_user)):
    workplace = Workplace(**workplace_creation.model_dump())
    await workplace.create()
    userAssignedWorkplace = UserAssignedWorkplace(user_id=user.id, workplace_id=workplace.id, role=Role.ADMIN)
    await userAssignedWorkplace.create()
    return SuccessfulResponse()


@router.get("/workplaces/{workplace_id}", response_model=Workplace, status_code=status.HTTP_200_OK)
async def get_workplace(workplace_id: UUID = Path(...), user: User = Depends(guest)):
    workplace = await Workplace.find(Workplace.id == workplace_id).first_or_none()
    if workplace is None:
        raise WorkplaceNotFoundError("Такого воркплейса не найдено.")
    return workplace


@router.put("/workplaces/{workplace_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_workplace(
    workplace_creation: WorkplaceCreation = Body(...), workplace_id: UUID = Path(...), user: User = Depends(admin)
):
    workplace = await Workplace.find(Workplace.id == workplace_id).first_or_none()
    if workplace is None:
        raise WorkplaceNotFoundError("Такого воркплейса не найдено.")
    await workplace.update({"$set": workplace_creation.model_dump()})
    return SuccessfulResponse()


@router.delete("/workplaces/{workplace_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_workplace(workplace_id: UUID = Path(...), user: User = Depends(admin)):
    workplace = await Workplace.find(Workplace.id == workplace_id).first_or_none()
    if workplace is None:
        raise WorkplaceNotFoundError("Такого воркплейса не найдено.")
    userAssignedWorkplaces = await UserAssignedWorkplace.find(
        UserAssignedWorkplace.workplace_id == workplace.id
    ).to_list()
    for userAssignedWorkplace in userAssignedWorkplaces:
        await userAssignedWorkplace.delete()
    await workplace.delete()
    return None
