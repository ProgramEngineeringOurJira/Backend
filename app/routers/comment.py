from typing import List
from uuid import UUID

from beanie import WriteRules
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import guest, member
from app.core.exceptions import CommentNotFoundError, ForbiddenException, IssueNotFoundError
from app.schemas.documents import Comment, Issue, UserAssignedWorkplace
from app.schemas.models import CommentCreation, SuccessfulResponse
from app.schemas.responses import CommentResponse

router = APIRouter(tags=["Comment"])


@router.post(
    "/{workplace_id}/issues/{issue_id}/comments", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED
)
async def create_comment(
    comment_creation: CommentCreation = Body(...),
    workplace_id: UUID = Path(...),
    issue_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    issue = await Issue.find_one(Issue.id == issue_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Указанная задача не найдена.")
    if issue.workplace.id != workplace_id:
        raise ForbiddenException("Указанная задача находится в другом воркпоейсе.")
    comment = Comment(**comment_creation.model_dump(), author=user)
    issue.comments.append(comment)
    await issue.save(link_rule=WriteRules.WRITE)
    return SuccessfulResponse()


@router.get(
    "/{workplace_id}/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_comment(
    comment_id: UUID = Path(...), workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)
):
    comment = await Comment.find_one(Comment.id == comment_id, fetch_links=True)
    if comment is None:
        raise CommentNotFoundError("Такого комментария не найдено.")
    if comment.issue.workplace.id != workplace_id:
        raise ForbiddenException("Указанный комментарий находится в другом воркплейсе.")
    return comment


@router.get(
    "/{workplace_id}/issues/{issue_id}/comments", response_model=List[CommentResponse], status_code=status.HTTP_200_OK
)
async def get_issue_comments(
    workplace_id: UUID = Path(...), issue_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)
):
    comments = await Comment.find(Comment.issue.id == issue_id, fetch_links=True).to_list()
    if len(comments) > 0 and comments[0].issue.workplace.id != workplace_id:
        raise ForbiddenException("Указанная задача находится в другом воркплейсе.")
    return comments


@router.put(
    "/{workplace_id}/comments/{comment_id}",
    response_model=SuccessfulResponse,
    status_code=status.HTTP_200_OK,
)
async def edit_comment(
    comment_creation: CommentCreation = Body(...),
    workplace_id: UUID = Path(...),
    comment_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    comment = await Comment.find_one(Comment.id == comment_id, fetch_links=True)
    if comment is None:
        raise CommentNotFoundError("Такого комментария не найдено.")
    if comment.issue.workplace.id != workplace_id:
        raise ForbiddenException("Указанный комментарий находится в другом воркплейсе.")
    await comment.update({"$set": comment_creation.model_dump()})
    return SuccessfulResponse()


@router.delete(
    "/{workplace_id}/comments/{comment_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    workplace_id: UUID = Path(...), comment_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(member)
):
    comment = await Comment.find_one(Comment.id == comment_id, fetch_links=True)
    if comment is None:
        raise CommentNotFoundError("Такого комментария не найдено.")
    if comment.issue.workplace.id != workplace_id:
        raise ForbiddenException("Указанный комментарий находится в другом воркплейсе.")
    await comment.delete()
    return None
