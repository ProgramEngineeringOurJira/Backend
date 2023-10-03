from typing import List
from uuid import UUID

from beanie import DeleteRules
from beanie.odm.documents import PydanticObjectId
from beanie.operators import In
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import guest, member
from app.core.exceptions import IssueNotFoundError, SprintNotFoundError, ValidationError
from app.routers.auth import User, UserAssignedWorkplace
from app.routers.auth.schemas import Role, SuccessfulResponse
from app.routers.sprint import Sprint

from .schemas import Issue, IssueCreation

router = APIRouter(tags=["Issue"])


@router.post("/{workplace_id}/issues", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_creation: IssueCreation = Body(...), workplace_id: UUID = Path(...), user: User = Depends(member)
):
    # TODO запрос к бд, что указанный статус есть в воркплейсе
    if issue_creation.sprint_id is not None:
        sprint = await Sprint.find_one(Sprint.id == issue_creation.sprint_id)
        if sprint is None:
            raise SprintNotFoundError("Такого спринта не найдено.")
        if sprint.workplace_id != workplace_id:
            raise ValidationError("Спринт должен находиться в том же воркплейсе.")
    issue = Issue(**issue_creation.model_dump(), workplace_id=workplace_id, author_id=user.id, implementers=list())
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
    # TODO запрос к бд, что указанный статус есть в ворплейсе
    if issue_creation.sprint_id is not None:
        sprint = await Sprint.find_one(Sprint.id == issue_creation.sprint_id)
        if sprint is None:
            raise SprintNotFoundError("Такого спринта не найдено.")
        if sprint.workplace_id != workplace_id:
            raise ValidationError("Спринт должен находиться в том же воркплейсе.")
    issue = await Issue.find_one(Issue.id == issue_id)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    await issue.update({"$set": issue_creation.model_dump()})
    return SuccessfulResponse()


@router.delete("/{workplace_id}/issues/{issue_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(issue_id: UUID = Path(...), user: User = Depends(member)):
    issue = await Issue.find_one(Issue.id == issue_id)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
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
    if len(await User.find(In(User.id, users_id)).to_list()) != len(users_id):
        raise ValidationError("Такого пользователя не существует.")
    # обещано что нижнее решит виталий
    if len(
        await UserAssignedWorkplace.find(
            UserAssignedWorkplace.workplace_id == workplace_id,
            In(UserAssignedWorkplace.user_id, users_id),
            UserAssignedWorkplace.role != Role.GUEST,
        ).to_list()
    ) != len(users_id):
        raise ValidationError("Задачу можно назначить только членам воркплейса.")

    issue = await Issue.find_one(Issue.id == issue_id)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    new_users = [id for id in users_id if id not in issue.implementers]
    issue.implementers.extend(new_users)
    await issue.save()
    return SuccessfulResponse()


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
