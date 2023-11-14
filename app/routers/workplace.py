from typing import List
from uuid import UUID, uuid4

from beanie import DeleteRules, WriteRules
from beanie.operators import In, RegEx
from fastapi import APIRouter, BackgroundTasks, Body, Depends, Path, Request, status
from fastapi.responses import RedirectResponse
from pydantic import EmailStr

from app.auth.oauth2 import admin, get_current_user, guest
from app.config import client_api_settings
from app.core.email import Email
from app.core.redis_session import Redis
from app.schemas.documents import Role, User, UserAssignedWorkplace, Workplace
from app.schemas.models import SuccessfulResponse, WorkplaceCreation

router = APIRouter(tags=["Workplace"])


@router.post("/workplace", response_model=SuccessfulResponse, status_code=status.HTTP_201_CREATED)
async def create_workplace(workplace_creation: WorkplaceCreation = Body(...), user: User = Depends(get_current_user)):
    workplace = Workplace(**workplace_creation.model_dump())
    workplace.users = [UserAssignedWorkplace(user=user, workplace_id=workplace.id, role=Role.ADMIN)]
    await workplace.save(link_rule=WriteRules.WRITE)
    return SuccessfulResponse()


@router.get(
    "/workplaces/{workplace_id}",
    response_model=Workplace,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
    response_model_exclude={"users"},
)
async def get_workplace(workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)):
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    return workplace


@router.put("/workplaces/{workplace_id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def edit_workplace(
    workplace_creation: WorkplaceCreation = Body(...),
    workplace_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(admin),
):
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
    await workplace.update({"$set": workplace_creation.model_dump()})
    return SuccessfulResponse()


@router.delete("/workplaces/{workplace_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_workplace(workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(admin)):
    await UserAssignedWorkplace.find(UserAssignedWorkplace.workplace.id == workplace_id).delete()
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    await workplace.delete(link_rule=DeleteRules.DELETE_LINKS)
    return None


@router.get(
    "/workplaces/{workplace_id}/users",
    response_model=List[UserAssignedWorkplace],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_users(
    prefix_email: str | None = "", workplace_id: UUID = Path(), user: UserAssignedWorkplace = Depends(guest)
):
    users = await UserAssignedWorkplace.find(
        UserAssignedWorkplace.workplace.id == workplace_id,
        RegEx(UserAssignedWorkplace.user.email, f"^{prefix_email}"),
        fetch_links=True,
    ).to_list()
    return users


@router.get(
    "/workplaces", response_model=List[Workplace], response_model_by_alias=False, status_code=status.HTTP_200_OK
)
async def get_user_workplaces(user: UserAssignedWorkplace = Depends(get_current_user)):
    workplaces = await Workplace.find(fetch_links=True).to_list()
    ids = [w.id for w in workplaces for u in w.users if u.user.id == user.id]
    workplaces = await Workplace.find(In(Workplace.id, ids), fetch_links=True).to_list()
    return workplaces


@router.get("/workplaces/{workplace_id}/invitation/{invitation_id}", status_code=status.HTTP_200_OK)
async def add_to_workplace(
    workplace_id: UUID = Path(...), redis: Redis = Depends(Redis), invitation_id: UUID = Path(...)
):
    new_user_email = await redis.get_invite_user_email(uuid=str(invitation_id))
    user = await User.by_email(new_user_email)
    # Если пользователь не вошёл или не зарегистрировался
    if not user:
        return RedirectResponse(client_api_settings.LOGIN_URL)
    # Если всё хорошо
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
    workplace.users.append(UserAssignedWorkplace(user=user, workplace_id=workplace.id, role=Role.MEMBER))
    await workplace.save(link_rule=WriteRules.WRITE)

    return RedirectResponse(client_api_settings.WORKPLACE_URL)


@router.post("/workplaces/{workplace_id}/invite", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def invite_to_workplace(
    request: Request,
    background_tasks: BackgroundTasks,
    email: Email = Depends(Email),
    new_user_email: EmailStr = Body(...),
    workplace_id: UUID = Path(...),
    redis: Redis = Depends(Redis),
    user: UserAssignedWorkplace = Depends(admin),
):
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
    invitation_id = str(uuid4())
    background_tasks.add_task(
        email.send_invitation_mail, request, new_user_email, workplace_id, invitation_id, workplace.name
    )
    await redis.set_uuid_invite_email(invitation_id, new_user_email)
    return SuccessfulResponse()
