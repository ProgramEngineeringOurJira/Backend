import pathlib
from uuid import UUID

from beanie import DeleteRules, WriteRules
from fastapi import APIRouter, BackgroundTasks, Body, Depends, Path, Request, UploadFile, status
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import EmailStr
from app.auth.jwt_token import decode_token

from app.auth.oauth2 import admin, get_current_user, guest, member, oauth2_scheme
from app.core.download import downloader
from app.core.email import Email
from app.core.exceptions import WorkplaceFileNotFoundException
from app.schemas.documents import Role, User, UserAssignedWorkplace, Workplace
from app.schemas.models import FileModelOut, SuccessfulResponse, WorkplaceCreation
from app.config import client_api_settings

router = APIRouter(tags=["InvitationWorkplace"])


@router.get("/workplaces/{workplace_id}/invitation", status_code=status.HTTP_200_OK)
async def add_to_workplace(workplace_id: UUID = Path(...), token: UUID = Depends(oauth2_scheme)):
    token = decode_token(token.credentials)
    user = await User.by_email(token.email)
    
    # Если пользователь не вошёл или не зарегистрировался
    if not user:
        return RedirectResponse(client_api_settings.MAIN_URL)
    
    # Если всё хорошо
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
    workplace.users.append(UserAssignedWorkplace(user=user, workplace_id=workplace.id, role=Role.MEMBER))
    await workplace.save(link_rule=WriteRules.WRITE)

    return RedirectResponse(f"/workplaces/{workplace_id}")


@router.post("/workplaces/{workplace_id}/invite", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
async def invite_to_workplace(
    request: Request,
    background_tasks: BackgroundTasks,
    email: Email = Depends(Email),
    new_user_email: EmailStr = Body(...),
    workplace_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(admin),
):
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
    background_tasks.add_task(email.sendInvitationMail, request, new_user_email, workplace_id, workplace.name)
    return SuccessfulResponse()