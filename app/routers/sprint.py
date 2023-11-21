from typing import List
from uuid import UUID

from beanie import WriteRules
from beanie.executors import Set
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import admin, guest
from app.core.exceptions import SprintNotFoundError
from app.schemas.documents import Issue, Sprint, SprintCreation, UserAssignedWorkplace, Workplace
from app.schemas.models import SuccessfulResponse

router = APIRouter(tags=["Sprint"])


@router.post("/{workplace_id}/sprints", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    sprint_creation: SprintCreation = Body(...),
    workplace_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(admin),
):
    await Sprint.validate_creation(sprint_creation, workplace_id)
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    workplace.sprints.append(Sprint(**sprint_creation.model_dump(), workplace_id=workplace.id))
    await workplace.save(link_rule=WriteRules.WRITE)
    return SuccessfulResponse()


@router.get(
    "/{workplace_id}/sprints/{sprint_id}",
    response_model=Sprint,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_sprint(
    workplace_id: UUID = Path(...), sprint_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)
):
    sprint = await Sprint.find_one(Sprint.id == sprint_id, Sprint.workplace_id == workplace_id, fetch_links=True)
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    return sprint


@router.get(
    "/{workplace_id}/sprints/list/{skip}/{limit}",
    response_model=List[Sprint],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_sprints(
    workplace_id: UUID = Path(...),
    skip: int = Path(...),
    limit: int = Path(...),
    user: UserAssignedWorkplace = Depends(guest),
):
    sprints = await Sprint.find(Sprint.workplace_id == workplace_id, fetch_links=True).skip(skip).limit(limit).to_list()
    return sprints


@router.put("/{workplace_id}/sprints/{sprint_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_sprint(
    sprint_creation: SprintCreation = Body(...),
    workplace_id: UUID = Path(...),
    sprint_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(admin),
):
    sprint = await Sprint.find_one(Sprint.workplace_id == workplace_id, Sprint.id == sprint_id)
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    await Sprint.validate_creation(sprint_creation, workplace_id, sprint_id)
    await sprint.update({"$set": sprint_creation.model_dump()})
    await Issue.find(Issue.sprint_id == sprint_id).update(Set({Issue.end_date: sprint_creation.end_date}))
    return SuccessfulResponse()


@router.delete("/{workplace_id}/sprints/{sprint_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(
    workplace_id: UUID = Path(...), sprint_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(admin)
):
    sprint = await Sprint.find_one(Sprint.workplace_id == workplace_id, Sprint.id == sprint_id, fetch_links=True)
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    await sprint.delete()
    return None
