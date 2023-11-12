from typing import List
from uuid import UUID

from asyncstdlib import list as alist
from asyncstdlib import map as amap
from beanie import WriteRules
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import guest, member
from app.core.exceptions import IssueNotFoundError, SprintNotFoundError, UserNotFoundError, ValidationError
from app.schemas.documents import Issue, Sprint, UserAssignedWorkplace, Workplace
from app.schemas.models import IssueCreation, SuccessfulResponse

router = APIRouter(tags=["Issue"])


@router.post("/{workplace_id}/issues", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_creation: IssueCreation = Body(...),
    workplace_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    sprint = await Sprint.find_one(
        Sprint.workplace.id == workplace_id, Sprint.id == issue_creation.sprint_id, fetch_links=True
    )
    implementers = await alist(amap(lambda id: UserAssignedWorkplace.get(id), issue_creation.implementers))
    if len(implementers) != len(issue_creation.implementers):
        raise UserNotFoundError("Пользователь не найден в воркплейсе")
    if not set(implementers).issubset(workplace.users):
        raise ValidationError("Пользователь не принадлежит worplace")
    if issue_creation.state not in workplace.states:
        raise ValidationError("Указанного статуса нет существует.")
    if sprint is None and issue_creation.sprint_id is not None:
        raise SprintNotFoundError("Нет такого спринта")
    issue = Issue(
        **issue_creation.model_dump(exclude={"implementers"}), author=user, implementers=implementers, sprint=None
    )
    if sprint is not None:
        sprint.issues.append(issue)
        await sprint.save(link_rule=WriteRules.WRITE)
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    workplace.issues.append(issue)
    await workplace.save(link_rule=WriteRules.WRITE)
    return SuccessfulResponse()


@router.get(
    "/{workplace_id}/issues/{issue_id}",
    response_model=Issue,
    status_code=status.HTTP_200_OK,
)
async def get_issue(
    workplace_id: UUID = Path(...), issue_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)
):
    issue = await Issue.find_one(Issue.workplace.id == workplace_id, Issue.id == issue_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    return issue


@router.get("/{workplace_id}/sprints/{sprint_id}/issues", response_model=List[Issue], status_code=status.HTTP_200_OK)
async def get_sprint_issues(
    workplace_id: UUID = Path(...), sprint_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)
):
    issue = await Issue.find(
        Issue.workplace.id == workplace_id, Issue.sprint.id == sprint_id, fetch_links=True
    ).to_list()
    return issue


@router.get("/{workplace_id}/issues", response_model=List[Issue], status_code=status.HTTP_200_OK)
async def get_workplace_issues(workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)):
    issue = await Issue.find(Issue.workplace.id == workplace_id, fetch_links=True).to_list()
    print(f"pidorasina {issue}")
    return issue


@router.put("/{workplace_id}/issues{issue_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_issue(
    issue_creation: IssueCreation = Body(...),
    workplace_id: UUID = Path(...),
    issue_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    issue = await Issue.find_one(Issue.workplace.id == workplace_id, Issue.id == issue_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    if issue_creation.state not in issue.workplace.states:
        raise ValidationError("Указанного статуса нет существует.")
    implementers = await alist(amap(lambda id: UserAssignedWorkplace.get(id), issue_creation.implementers))
    if len(implementers) != len(issue_creation.implementers):
        raise UserNotFoundError("Пользователь не найден в воркплейсе")
    if not set(implementers).issubset(issue.workplace.users):
        raise ValidationError("Пользователь не принадлежит worplace")
    if issue_creation.sprint_id is not None:
        # блядь None не робит я в ахуе issue создан в либу, убейте меня время 5 утра я в щи, баскетбол ногой...
        if issue.sprint is None or issue_creation.sprint_id != issue.sprint.id:
            issue.sprint.issues.remove(issue.id)
            sprint = await Sprint.find_one(
                Sprint.workplace.id == workplace_id, Sprint.id == issue_creation.sprint_id, fetch_links=True
            )
            sprint.issues.append(issue)
            await sprint.save(link_rule=WriteRules.WRITE)
    else:
        issue.sprint.issue.remove(issue.id)
    issue.implementers = implementers
    await issue.update({"$set": issue_creation.model_dump(exclude="author,implementers")})
    return SuccessfulResponse()


@router.delete("/{workplace_id}/issues/{issue_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(
    workplace_id: UUID = Path(...), issue_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(member)
):
    issue = await Issue.find_one(Issue.workplace.id == workplace_id, Issue.id == issue_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    await issue.delete()
    return None
