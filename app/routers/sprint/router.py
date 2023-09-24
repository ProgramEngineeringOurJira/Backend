from uuid import UUID

from app.auth.oauth2 import admin, guest
from app.core.exceptions import SprintNotFoundError
from app.routers.auth import User
from fastapi import APIRouter, Body, Depends, Path, status

from .schemas import Sprint, SprintCreation, SuccessfulResponse

router = APIRouter(tags=["Sprint"])


@router.post("/{workplace_id}/createsprint", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def create(
    sprint_creation: SprintCreation = Body(...), workplace_id: UUID = Path(...), user: User = Depends(admin)
):
    # TODO Проверить что существует workplace c id

    sprint = Sprint(**sprint_creation.model_dump(), workplace_id=workplace_id)
    await sprint.create()
    return SuccessfulResponse()


@router.get("/{workplace_id}/sprints/{sprint_id}", response_model=Sprint, status_code=status.HTTP_200_OK)
async def get(sprint_id: UUID = Path(...), user: User = Depends(guest)):
    sprint = await Sprint.find(Sprint.id == sprint_id).first_or_none()
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    return sprint


@router.put("/{workplace_id}/sprints/{sprint_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit(sprint_creation: SprintCreation = Body(...), sprint_id: UUID = Path(...), user: User = Depends(admin)):
    sprint = await Sprint.find(Sprint.id == sprint_id).first_or_none()
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    await sprint.update({"$set": sprint_creation.model_dump()})
    return SuccessfulResponse()


@router.delete("/{workplace_id}/sprints/{sprint_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def delete(sprint_id: UUID = Path(...), user: User = Depends(admin)):
    sprint = await Sprint.find(Sprint.id == sprint_id).first_or_none()
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    sprint.delete()
    return SuccessfulResponse()
