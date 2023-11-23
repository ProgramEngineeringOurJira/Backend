from typing import List
from uuid import UUID

from asyncstdlib import list as alist
from asyncstdlib import map as amap
from beanie import WriteRules
from beanie.operators import Set
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import guest, member
from app.core.exceptions import IssueNotFoundError, SprintNotFoundError, UserNotFoundError, ValidationError
from app.schemas.documents import Comment, Issue, Sprint, UserAssignedWorkplace
from app.schemas.models import IssueCreation, SuccessfulResponse

router = APIRouter(tags=["Issue"])


@router.post("/{workplace_id}/issues", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_creation: IssueCreation = Body(...),
    workplace_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    sprint = await Sprint.find_one(
        Sprint.workplace_id == workplace_id, Sprint.id == issue_creation.sprint_id, fetch_links=True
    )
    if sprint is None:
        raise SprintNotFoundError("Нет такого спринта")
    workplace = sprint.workplace
    implementers = await alist(amap(lambda id: UserAssignedWorkplace.get(id), issue_creation.implementers))
    if len(implementers) != len(issue_creation.implementers):
        raise UserNotFoundError("Пользователь не найден в воркплейсе")
    if not set(implementers).issubset(workplace.users):
        raise ValidationError("Пользователь не принадлежит worplace")
    issue = Issue(
        **issue_creation.model_dump(exclude={"implementers"}),
        author=user,
        implementers=implementers,
        workplace_id=workplace_id,
        end_date=sprint.end_date
    )
    sprint.issues.append(issue)
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
    issue = await Issue.find_one(Issue.id == issue_id, Issue.workplace_id == workplace_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
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
    sprint = await Sprint.find_one(Sprint.workplace_id == workplace_id, Sprint.id == sprint_id, fetch_links=True)
    if sprint is None:
        raise SprintNotFoundError("Нет такого спринта")
    return sprint.issues


@router.get(
    "/{workplace_id}/issues", response_model=List[Issue], response_model_by_alias=False, status_code=status.HTTP_200_OK
)
async def get_workplace_issues(workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)):
    issues = await Issue.find(Issue.workplace_id == workplace_id, fetch_links=True).to_list()
    return issues


@router.put("/{workplace_id}/issues{issue_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_issue(
    issue_creation: IssueCreation = Body(...),
    workplace_id: UUID = Path(...),
    issue_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    issue = await Issue.find_one(Issue.id == issue_id, Issue.workplace_id == workplace_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    implementers = await alist(amap(lambda id: UserAssignedWorkplace.get(id), issue_creation.implementers))
    if len(implementers) != len(issue_creation.implementers):
        raise UserNotFoundError("Пользователь не найден в воркплейсе")
    if not set(implementers).issubset(issue.sprint.workplace.users):
        raise ValidationError("Пользователь не принадлежит worplace")
    if issue_creation.sprint_id != issue.sprint_id:
        sprint = await Sprint.find_one(
            Sprint.workplace_id == workplace_id, Sprint.id == issue_creation.sprint_id, fetch_links=False
        )  # именно False!
        if sprint is None:
            raise SprintNotFoundError("Нет такого спринта")
        issue.sprint.issues.remove(issue.id)
        await issue.sprint.save(link_rule=WriteRules.WRITE)
        sprint.issues.append(issue)
        issue.end_date = sprint.end_date
        await sprint.save(link_rule=WriteRules.WRITE)
    issue.implementers = implementers
    await issue.update({"$set": issue_creation.model_dump(exclude="author,implementers")})
    await Comment.find(Comment.issue_id == issue_id).update(Set({Comment.sprint_id: issue_creation.sprint_id}))
    return SuccessfulResponse()


@router.delete("/{workplace_id}/issues/{issue_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    workplace_id: UUID = Path(...), issue_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(member)
):
    issue = await Issue.find_one(Issue.id == issue_id, Issue.workplace_id == workplace_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    await issue.delete()
    return None
