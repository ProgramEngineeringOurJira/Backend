from typing import List
from uuid import UUID

from beanie.odm.operators.find.logical import And, Or
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import admin, guest
from app.core.exceptions import SprintNotFoundError, ValidationError
from app.routers.auth import User
from app.schemas.documents import Sprint, SprintCreation, Workplace
from app.schemas.models.models import SuccessfulResponse

router = APIRouter(tags=["Sprint"])


@router.post("/{workplace_id}/sprints", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    sprint_creation: SprintCreation = Body(...), workplace_id: UUID = Path(...), user: User = Depends(admin)
):
    sprint = Sprint(**sprint_creation.model_dump(), workplace_id=workplace_id)
    find_sprint = await Sprint.find_one(
        Sprint.workplace_id == workplace_id,
        Or(
            And(Sprint.start_date >= sprint_creation.start_date, Sprint.start_date < sprint_creation.end_date),
            And(Sprint.end_date > sprint_creation.start_date, Sprint.end_date <= sprint_creation.end_date),
            And(Sprint.start_date <= sprint_creation.start_date, Sprint.end_date >= sprint_creation.end_date),
        ),
    )
    if find_sprint is not None:
        raise ValidationError("Спринты не должны пересекаться по дате.")
    await sprint.create()
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    workplace.sprints.append(sprint)
    await workplace.save()
    return SuccessfulResponse()


@router.get("/{workplace_id}/sprints/{sprint_id}", response_model=Sprint, status_code=status.HTTP_200_OK)
async def get_sprint(sprint_id: UUID = Path(...), user: User = Depends(guest)):
    sprint = await Sprint.find(Sprint.id == sprint_id).first_or_none()
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    return sprint


@router.get("/{workplace_id}/sprints/{skip}/{limit}", response_model=List[Sprint], status_code=status.HTTP_200_OK)
async def get_sprints(
    workplace_id: UUID = Path(...), skip: int = Path(...), limit: int = Path(...), user: User = Depends(guest)
):
    sprints = await Sprint.find_all(Sprint.workplace_id == workplace_id).skip(skip).limit(limit).to_list()
    return sprints


@router.put("/{workplace_id}/sprints/{sprint_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_sprint(
    sprint_creation: SprintCreation = Body(...),
    workplace_id: UUID = Path(...),
    sprint_id: UUID = Path(...),
    user: User = Depends(admin),
):
    sprint = await Sprint.find_one(Sprint.id == sprint_id)
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    find_sprint = await Sprint.find_one(
        Sprint.workplace_id == workplace_id,
        Sprint.id != sprint_id,
        Or(
            And(Sprint.start_date >= sprint_creation.start_date, Sprint.start_date < sprint_creation.end_date),
            And(Sprint.end_date > sprint_creation.start_date, Sprint.end_date <= sprint_creation.end_date),
            And(Sprint.start_date <= sprint_creation.start_date, Sprint.end_date >= sprint_creation.end_date),
        ),
    )
    if find_sprint is not None:
        raise ValidationError("Спринты не должны пересекаться по дате.")
    await sprint.update({"$set": sprint_creation.model_dump()})
    return SuccessfulResponse()


@router.delete("/{workplace_id}/sprints/{sprint_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(workplace_id: UUID = Path(...), sprint_id: UUID = Path(...), user: User = Depends(admin)):
    sprint = await Sprint.find_one(Sprint.id == sprint_id, fetch_links=True)
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    for issue in sprint.issues:
        issue.sprint_id = None
        await issue.save()
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    workplace.sprints.remove(sprint)
    await workplace.save()
    await sprint.delete()
    return None
