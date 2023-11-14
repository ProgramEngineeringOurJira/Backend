import itertools
from typing import List
from uuid import UUID

from asyncstdlib import list as alist
from asyncstdlib import map as amap
from beanie import WriteRules
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import guest, member
from app.core.exceptions import (
    ForbiddenException,
    IssueNotFoundError,
    SprintNotFoundError,
    UserNotFoundError,
    ValidationError,
)
from app.schemas.documents import Issue, Sprint, UserAssignedWorkplace
from app.schemas.models import IssueCreation, SuccessfulResponse

router = APIRouter(tags=["Issue"])


@router.post("/{workplace_id}/issues", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_creation: IssueCreation = Body(...),
    workplace_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    sprint = await Sprint.find_one(
        Sprint.workplace.id == workplace_id, Sprint.id == issue_creation.sprint_id, fetch_links=True
    )
    if sprint is None:
        raise SprintNotFoundError("Нет такого спринта")
    workplace = sprint.workplace
    implementers = await alist(amap(lambda id: UserAssignedWorkplace.get(id), issue_creation.implementers))
    if len(implementers) != len(issue_creation.implementers):
        raise UserNotFoundError("Пользователь не найден в воркплейсе")
    if not set(implementers).issubset(workplace.users):
        raise ValidationError("Пользователь не принадлежит worplace")
    if issue_creation.state not in workplace.states:
        raise ValidationError("Указанного статуса нет существует.")
    issue = Issue(**issue_creation.model_dump(exclude={"implementers"}), author=user, implementers=implementers)
    sprint.issues.append(issue)
    issue.end_date = sprint.end_date
    await sprint.save(link_rule=WriteRules.WRITE)
    return SuccessfulResponse()


@router.get(
    "/{workplace_id}/issues/{issue_id}",
    response_model=Issue,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_issue(
    workplace_id: UUID = Path(...), issue_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)
):
    issue = await Issue.find_one(Issue.id == issue_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    if issue.sprint.workplace.id != workplace_id:
        raise ForbiddenException("Указанная задача находится в другом воркпоейсе.")
    return issue


@router.get(
    "/{workplace_id}/sprints/{sprint_id}/issues",
    response_model=List[Issue],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_sprint_issues(
    workplace_id: UUID = Path(...), sprint_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)
):
    sprint = await Sprint.find_one(Sprint.workplace.id == workplace_id, Sprint.id == sprint_id, fetch_links=True)
    if sprint is None:
        raise SprintNotFoundError("Нет такого спринта")
    return sprint.issues


@router.get(
    "/{workplace_id}/issues", response_model=List[Issue], response_model_by_alias=False, status_code=status.HTTP_200_OK
)
async def get_workplace_issues(workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)):
    sprints = await Sprint.find(Sprint.workplace.id == workplace_id, fetch_links=True).to_list()
    list_issues = [sprint.issues for sprint in sprints]
    return list(itertools.chain.from_iterable(list_issues))


@router.put("/{workplace_id}/issues{issue_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_issue(
    issue_creation: IssueCreation = Body(...),
    workplace_id: UUID = Path(...),
    issue_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    issue = await Issue.find_one(Issue.id == issue_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    if issue.sprint.workplace.id != workplace_id:
        raise ForbiddenException("Указанная задача находится в другом воркпоейсе.")
    if issue_creation.state not in issue.sprint.workplace.states:
        raise ValidationError("Указанного статуса нет существует.")
    implementers = await alist(amap(lambda id: UserAssignedWorkplace.get(id), issue_creation.implementers))
    if len(implementers) != len(issue_creation.implementers):
        raise UserNotFoundError("Пользователь не найден в воркплейсе")
    if not set(implementers).issubset(issue.sprint.workplace.users):
        raise ValidationError("Пользователь не принадлежит worplace")
    if issue_creation.sprint_id != issue.sprint.id:
        sprint = await Sprint.find_one(
            Sprint.workplace.id == workplace_id, Sprint.id == issue_creation.sprint_id, fetch_links=True
        )
        if sprint is None:
            raise SprintNotFoundError("Нет такого спринта")
        issue.sprint.issues.remove(issue.id)
        await issue.save(link_rule=WriteRules.WRITE)
        sprint.issues.append(issue)
        issue.end_date = sprint.end_date
        await sprint.save(link_rule=WriteRules.WRITE)
    issue.implementers = implementers
    await issue.update({"$set": issue_creation.model_dump(exclude="author,implementers")})
    return SuccessfulResponse()


@router.delete("/{workplace_id}/issues/{issue_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    workplace_id: UUID = Path(...), issue_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(member)
):
    issue = await Issue.find_one(Issue.id == issue_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    if issue.sprint.workplace.id != workplace_id:
        raise ForbiddenException("Указанная задача находится в другом воркпоейсе.")
    await issue.delete()
    return None
