from typing import List
from uuid import UUID

from beanie import WriteRules
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import admin, guest
from app.core.exceptions import SprintNotFoundError
from app.schemas.documents import Sprint, UserAssignedWorkplace, Workplace
from app.schemas.models import SprintCreation, SprintUpdate, SuccessfulResponse
from app.schemas.models.responses import Column, SprintResponse

router = APIRouter(tags=["Sprint"])


@router.post("/{workplace_id}/sprints", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    sprint_creation: SprintCreation = Body(...),
    workplace_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(admin),
):
    await Sprint.validate_dates(sprint_creation.start_date, sprint_creation.end_date, workplace_id)
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    workplace.sprints.append(Sprint(**sprint_creation.model_dump(), workplace_id=workplace.id))
    await workplace.save(link_rule=WriteRules.WRITE)
    return SuccessfulResponse()


@router.get(
    "/{workplace_id}/sprints/{sprint_id}",
    response_model=SprintResponse,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_sprint(
    workplace_id: UUID = Path(...), sprint_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)
):
    sprint = await Sprint.find_one(Sprint.id == sprint_id, Sprint.workplace_id == workplace_id, fetch_links=True)
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    issues = Column.group(sprint.issues)
    return SprintResponse(**sprint.model_dump(), columns=issues)


@router.get(
    "/{workplace_id}/sprints",
    response_model=List[Sprint],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_sprints(
    workplace_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(guest),
):
    sprints = await Sprint.find(Sprint.workplace_id == workplace_id, fetch_links=True).to_list()
    return sprints


@router.put("/{workplace_id}/sprints/{sprint_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_sprint(
    sprint_update: SprintUpdate = Body(...),
    workplace_id: UUID = Path(...),
    sprint_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(admin),
):
    sprint = await Sprint.find_one(Sprint.workplace_id == workplace_id, Sprint.id == sprint_id)
    if sprint is None:
        raise SprintNotFoundError("Такого спринта не найдено.")
    start_date = sprint.start_date if sprint_update.start_date is None else sprint_update.start_date
    end_date = sprint.end_date if sprint_update.end_date is None else sprint_update.end_date
    await Sprint.validate_dates(start_date, end_date, workplace_id, sprint_id)
    await sprint.update({"$set": sprint_update.model_dump(exclude_none=True)})
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
