import pathlib
from os import makedirs
from uuid import UUID

from fastapi import UploadFile

from app.core.storage import get_workplace_storage


class DownloadFiles:
    async def __call__(self, file: UploadFile, workplace_id: UUID) -> dict:
        async def download_file(file: UploadFile, workplace_id: UUID) -> dict:
            main_download_folder = get_workplace_storage()
            workplace_download_folder = main_download_folder.joinpath(pathlib.Path(f"{workplace_id}"))
            makedirs(main_download_folder, exist_ok=True)
            makedirs(workplace_download_folder, exist_ok=True)
            photo_path = workplace_download_folder.joinpath(pathlib.Path(f"{file.filename}"))
            with open(photo_path, "wb+") as file_object:
                file_object.write(file.file.read())
            return file.filename

        return await download_file(file, workplace_id)


downloader = DownloadFiles()
