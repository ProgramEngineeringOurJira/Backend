from typing import List
from uuid import UUID

from beanie import DeleteRules
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import guest, member
from app.core.exceptions import IssueNotFoundError
from app.queries.issue import create_new_issue, update_issue
from app.schemas.documents import Issue, Sprint, User
from app.schemas.models.models import IssueCreation, SuccessfulResponse

router = APIRouter(tags=["Issue"])


@router.post("/{workplace_id}/issues", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_creation: IssueCreation = Body(...), workplace_id: UUID = Path(...), user: User = Depends(member)
):
    await create_new_issue(issue_creation, workplace_id, user)
    return SuccessfulResponse()


@router.get(
    "/{workplace_id}/issues/{issue_id}",
    response_model=Issue,
    status_code=status.HTTP_200_OK,
)
async def get_issue(issue_id: UUID = Path(...), user: User = Depends(guest)):
    issue = await Issue.find_one(Issue.id == issue_id, fetch_links=True)
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
    update_issue(issue_creation, workplace_id, issue_id, user)
    return SuccessfulResponse()


@router.delete("/{workplace_id}/issues/{issue_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(issue_id: UUID = Path(...), user: User = Depends(member)):
    issue = await Issue.find_one(Issue.id == issue_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    if isinstance(issue.sprint, Sprint):
        sprint = issue.sprint
        sprint.issues.remove(issue)
        await sprint.save()
    workplace = issue.workplace
    workplace.issues.remove(issue)
    await workplace.save()
    await issue.delete(link_rule=DeleteRules.DO_NOTHING)
    return None
