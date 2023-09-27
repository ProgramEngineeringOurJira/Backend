<<<<<<< HEAD
from uuid import UUID

from app.auth.roles import admin, guest
from app.core.exceptions import SprintNotFoundError
from app.routers.auth import User
from fastapi import APIRouter, Body, Depends, Path, status

from .schemas import Sprint, SprintCreation, SuccessfulResponse
=======
from typing import List
from uuid import UUID

from app.auth.oauth2 import admin, guest
from app.core.exceptions import SprintNotFoundError, ValidationError
from app.routers.auth import User
from app.routers.auth.schemas import SuccessfulResponse
from beanie.odm.operators.find.logical import And, Or
from fastapi import APIRouter, Body, Depends, Path, status

from .schemas import Sprint, SprintCreation
>>>>>>> origin/dev

router = APIRouter(tags=["Sprint"])


<<<<<<< HEAD
@router.post("/{workplace_id}/createsprint", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def create(
    sprint_creation: SprintCreation = Body(...), workplace_id: UUID = Path(...), user: User = Depends(admin)
):
    # TODO Проверить что существует workplace c id

    sprint = Sprint(**sprint_creation.model_dump(), workplace_id=workplace_id)
=======
@router.post("/{workplace_id}/sprints", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    sprint_creation: SprintCreation = Body(...), workplace_id: UUID = Path(...), user: User = Depends(admin)
):
    sprint = Sprint(**sprint_creation.model_dump(), workplace_id=workplace_id)
    find_sprint = await Sprint.find(
        Or(
            And(Sprint.start_date >= sprint_creation.start_date, Sprint.start_date < sprint_creation.end_date),
            And(Sprint.end_date > sprint_creation.start_date, Sprint.end_date <= sprint_creation.end_date),
            And(Sprint.start_date <= sprint_creation.start_date, Sprint.end_date >= sprint_creation.end_date),
        )
    ).first_or_none()
    if find_sprint is not None:
        raise ValidationError("Спринты не должны пересекаться по дате.")
>>>>>>> origin/dev
    await sprint.create()
    return SuccessfulResponse()


@router.get("/{workplace_id}/sprints/{sprint_id}", response_model=Sprint, status_code=status.HTTP_200_OK)
<<<<<<< HEAD
async def get(sprint_id: UUID = Path(...), user: User = Depends(guest)):
=======
async def get_sprint(sprint_id: UUID = Path(...), user: User = Depends(guest)):
>>>>>>> origin/dev
    sprint = await Sprint.find(Sprint.id == sprint_id).first_or_none()
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    return sprint


<<<<<<< HEAD
@router.put("/{workplace_id}/sprints/{sprint_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit(sprint_creation: SprintCreation = Body(...), sprint_id: UUID = Path(...), user: User = Depends(admin)):
    sprint = await Sprint.find(Sprint.id == sprint_id).first_or_none()
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
=======
@router.get("/{workplace_id}/sprints/{skip}/{limit}", response_model=List[Sprint], status_code=status.HTTP_200_OK)
async def get_sprints(
    workplace_id: UUID = Path(...), skip: int = Path(...), limit: int = Path(...), user: User = Depends(guest)
):
    sprints = await Sprint.find_all(Sprint.workplace_id == workplace_id).skip(skip).limit(limit).to_list()
    return sprints


@router.put("/{workplace_id}/sprints/{sprint_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_sprint(
    sprint_creation: SprintCreation = Body(...), sprint_id: UUID = Path(...), user: User = Depends(admin)
):
    sprint = await Sprint.find(Sprint.id == sprint_id).first_or_none()
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    find_sprint = await Sprint.find(
        Sprint.id != sprint_id,
        Or(
            And(Sprint.start_date >= sprint_creation.start_date, Sprint.start_date < sprint_creation.end_date),
            And(Sprint.end_date > sprint_creation.start_date, Sprint.end_date <= sprint_creation.end_date),
            And(Sprint.start_date <= sprint_creation.start_date, Sprint.end_date >= sprint_creation.end_date),
        ),
    ).first_or_none()
    if find_sprint is not None:
        raise ValidationError("Спринты не должны пересекаться по дате.")
>>>>>>> origin/dev
    await sprint.update({"$set": sprint_creation.model_dump()})
    return SuccessfulResponse()


<<<<<<< HEAD
@router.delete("/{workplace_id}/sprints/{sprint_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def delete(sprint_id: UUID = Path(...), user: User = Depends(admin)):
    sprint = await Sprint.find(Sprint.id == sprint_id).first_or_none()
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    sprint.delete()
    return SuccessfulResponse()
=======
@router.delete("/{workplace_id}/sprints/{sprint_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(sprint_id: UUID = Path(...), user: User = Depends(admin)):
    sprint = await Sprint.find(Sprint.id == sprint_id).first_or_none()
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    await sprint.delete()
    return None
>>>>>>> origin/dev
