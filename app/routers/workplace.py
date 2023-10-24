import pathlib
from uuid import UUID

from beanie import DeleteRules, WriteRules
from fastapi import APIRouter, Body, Depends, Path, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from app.auth.oauth2 import admin, get_current_user, guest, member
from app.core.download import downloader
from app.core.exceptions import WorkplaceFileNotFoundException
from app.schemas.documents import Role, User, UserAssignedWorkplace, Workplace
from app.schemas.models import SuccessfulResponse, WorkplaceCreation, FileModelOut

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
    response_model_exclude={"users"},
)
async def get_workplace(workplace_id: UUID = Path(...), user: UserAssignedWorkplace = Depends(guest)):
    workplace = await Workplace.find_one(Workplace.id == workplace_id)
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


@router.post("/workplaces/{workplace_id}/file", status_code=status.HTTP_201_CREATED, response_model=FileModelOut)
async def add_file(
    file_to_upload: UploadFile,
    workplace_id: UUID = Path(...),
    user: UserAssignedWorkplace = Depends(member),
):
    filename: str = await downloader(file_to_upload, workplace_id)
    url = f"/workplaces/{workplace_id}/file/{filename}"
    fileModelOut = FileModelOut(url)
    return fileModelOut


@router.get("/workplaces/{workplace_id}/file/{filename}", status_code=status.HTTP_200_OK)
async def get_file(
    workplace_id: UUID = Path(...), filename: str = Path(...), user: UserAssignedWorkplace = Depends(member)
):
    local_storage = pathlib.Path(__file__).parent.parent.parent.resolve()
    path_file = local_storage.joinpath(pathlib.Path(f"assets/{workplace_id}/{filename}"))
    if not pathlib.Path.is_file(path_file):
        raise WorkplaceFileNotFoundException("Файл не найден")
    return FileResponse(path_file)
