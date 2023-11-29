from typing import List
from uuid import UUID

from beanie import WriteRules
from fastapi import APIRouter, Body, Depends, Path, status

from app.auth.oauth2 import guest, member
from app.core.exceptions import CommentNotFoundError, IssueNotFoundError
from app.schemas.documents import Comment, Issue, UserAssignedWorkplace
from app.schemas.models import CommentCreation, CommentUpdate, CreationResponse, SuccessfulResponse

router = APIRouter(tags=["Comment"])


@router.post(
    "/{workplace_id}/issues/{issue_id}/comments", response_model=CreationResponse, status_code=status.HTTP_201_CREATED
)
async def create_comment(
    comment_creation: CommentCreation = Body(...),
    workplace_id: UUID = Path(...),
    issue_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    issue = await Issue.find_one(Issue.id == issue_id, Issue.workplace_id == workplace_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Указанная задача не найдена.")
    comment = Comment(
        **comment_creation.model_dump(),
        author=user,
        issue_id=issue_id,
        sprint_id=issue.sprint_id,
        workplace_id=workplace_id
    )
    issue.comments.append(comment)
    await issue.save(link_rule=WriteRules.WRITE)
    return CreationResponse(id=comment.id)


@router.get(
    "/{workplace_id}/comments/{comment_id}",
    response_model=Comment,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_comment(
    comment_id: UUID = Path(...), workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)
):
    comment = await Comment.find_one(Comment.id == comment_id, Issue.workplace_id == workplace_id, fetch_links=True)
    if comment is None:
        raise CommentNotFoundError("Такого комментария не найдено.")
    return comment


@router.get(
    "/{workplace_id}/issues/{issue_id}/comments",
    response_model=List[Comment],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_issue_comments(
    workplace_id: UUID = Path(...), issue_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)
):
    comments = await Comment.find(
        Comment.issue_id == issue_id, Comment.workplace_id == workplace_id, fetch_links=True
    ).to_list()
    return comments


@router.put(
    "/{workplace_id}/comments/{comment_id}",
    response_model=SuccessfulResponse,
    status_code=status.HTTP_200_OK,
)
async def edit_comment(
    comment_update: CommentUpdate = Body(...),
    workplace_id: UUID = Path(...),
    comment_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    comment = await Comment.find_one(Comment.id == comment_id, Comment.workplace_id == workplace_id, fetch_links=True)
    if comment is None:
        raise CommentNotFoundError("Такого комментария не найдено.")
    await comment.update({"$set": comment_update.model_dump(exclude_none=True)})
    return SuccessfulResponse()


@router.delete(
    "/{workplace_id}/comments/{comment_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    workplace_id: UUID = Path(...), comment_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(member)
):
    comment = await Comment.find_one(Comment.id == comment_id, Comment.workplace_id == workplace_id, fetch_links=True)
    if comment is None:
        raise CommentNotFoundError("Такого комментария не найдено.")
    await comment.delete()
    return None
