from typing import List
from uuid import UUID

from beanie import DeleteRules
from beanie.odm.documents import PydanticObjectId
from beanie.operators import In
from bson import Binary, UuidRepresentation
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import guest, member
from app.core.exceptions import IssueNotFoundError, SprintNotFoundError, ValidationError
from app.schemas.auth import SuccessfulResponse, User
from app.schemas.sprint import Sprint
from app.schemas.workplace import Role, Workplace

from ..schemas.issue import Issue, IssueCreation

router = APIRouter(tags=["Issue"])


@router.post("/{workplace_id}/issues", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_creation: IssueCreation = Body(...), workplace_id: UUID = Path(...), user: User = Depends(member)
):
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
    if issue_creation.state not in workplace.states:
        raise ValidationError("Указанного статуса не существует.")
    issue = Issue(**issue_creation.model_dump(), workplace_id=workplace_id, author_id=user.id)
    if issue_creation.sprint_id is not None:
        sprint = await Sprint.find_one(Sprint.id == issue_creation.sprint_id)
        if sprint is None:
            raise SprintNotFoundError("Такого спринта не найдено.")
        if sprint.workplace_id != workplace_id:
            raise ValidationError("Спринт должен находиться в том же воркплейсе.")
        sprint.issues.append(Issue.link_from_id(Binary.from_uuid(issue.id, UuidRepresentation.STANDARD)))
        await sprint.save()
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
    workplace.issues.append(Issue.link_from_id(Binary.from_uuid(issue.id, UuidRepresentation.STANDARD)))
    await workplace.save()
    await issue.create()
    return SuccessfulResponse()


@router.get("/{workplace_id}/issues/{issue_id}", response_model=Issue, status_code=status.HTTP_200_OK)
async def get_issue(issue_id: UUID = Path(...), user: User = Depends(guest)):
    issue = await Issue.find_one(Issue.id == issue_id)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    return issue


@router.get("/{workplace_id}/sprints/{sprint_id}/issues", response_model=List[Issue], status_code=status.HTTP_200_OK)
async def get_sprint_issues(sprint_id: UUID = Path(...), user: User = Depends(guest)):
    issue = await Issue.find(Issue.sprint_id == sprint_id).to_list()
    return issue


@router.get("/{workplace_id}/issues", response_model=List[Issue], status_code=status.HTTP_200_OK)
async def get_workplace_issues(workplace_id: UUID = Path(...), user: User = Depends(guest)):
    issue = await Issue.find(Issue.workplace_id == workplace_id).to_list()
    return issue


@router.put("/{workplace_id}/issues{issue_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_issue(
    issue_creation: IssueCreation = Body(...),
    workplace_id: UUID = Path(...),
    issue_id: UUID = Path(...),
    user: User = Depends(member),
):
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
    if issue_creation.state not in workplace.states:
        raise ValidationError("Указанного статуса нет существует.")
    issue = await Issue.find_one(Issue.id == issue_id)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    link = Issue.link_from_id(Binary.from_uuid(issue.id, UuidRepresentation.STANDARD))
    if issue_creation.sprint_id != issue.sprint_id:
        if issue.sprint_id is not None:
            old_sprint = await Sprint.find_one(Sprint.id == issue.sprint_id)
            old_sprint.issues = [iss for iss in old_sprint.issues if iss.ref != link.ref]
            await old_sprint.save()
        if issue_creation.sprint_id is not None:
            sprint = await Sprint.find_one(Sprint.id == issue_creation.sprint_id)
            if sprint is None:
                raise SprintNotFoundError("Такого спринта не найдено.")
            if sprint.workplace_id != workplace_id:
                raise ValidationError("Спринт должен находиться в том же воркплейсе.")
            sprint.issues.append(link)
            await sprint.save()
    await issue.update({"$set": issue_creation.model_dump()})
    return SuccessfulResponse()


@router.delete("/{workplace_id}/issues/{issue_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(issue_id: UUID = Path(...), user: User = Depends(member)):
    issue = await Issue.find_one(Issue.id == issue_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    link = Issue.link_from_id(Binary.from_uuid(issue.id, UuidRepresentation.STANDARD))
    if issue.sprint_id is not None:
        sprint = await Sprint.find_one(Sprint.id == issue.sprint_id)
        sprint.issues = [iss for iss in sprint.issues if iss.ref != link.ref]
        await sprint.save()
    workplace = await Workplace.find_one(Workplace.id == issue.workplace_id)
    workplace.issues = [iss for iss in workplace.issues if iss.ref != link.ref]
    await workplace.save()
    await issue.delete(link_rule=DeleteRules.DELETE_LINKS)
    return None


@router.post(
    "/{workplace_id}/issues/{issue_id}/users",
    response_model=SuccessfulResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_users(
    users_id: List[PydanticObjectId] = Body(...),
    workplace_id: UUID = Path(...),
    issue_id: UUID = Path(...),
    user: User = Depends(member),
):
    if await User.find(In(User.id, users_id)).count() != len(users_id):
        raise ValidationError("Указанного пользователя не существует.")
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    workplace_users = [usr.user_id for usr in workplace.users if usr.role != Role.GUEST]
    if len([id for id in users_id if id in workplace_users]) != len(users_id):
        raise ValidationError("Задачу можно назначить только членам воркплейса.")
    issue = await Issue.find_one(Issue.id == issue_id)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    new_users = [id for id in users_id if id not in issue.implementers]
    issue.implementers.extend(new_users)
    await issue.save()
    return SuccessfulResponse()


# TODO скрыть пароль
@router.get("/{workplace_id}/issues/{issue_id}/users", response_model=List[User], status_code=status.HTTP_200_OK)
async def get_users(issue_id: UUID = Path(...), user: User = Depends(member)):
    issue = await Issue.find_one(Issue.id == issue_id)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    users = await User.find(In(User.id, issue.implementers)).to_list()
    return users


@router.delete("/{workplace_id}/issues/{issue_id}/users", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def unassign_users(
    users_id: List[PydanticObjectId] = Body(...), issue_id: UUID = Path(...), user: User = Depends(member)
):
    issue = await Issue.find_one(Issue.id == issue_id)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    issue.implementers = [user_id for user_id in issue.implementers if user_id not in users_id]
    await issue.save()
    return None
