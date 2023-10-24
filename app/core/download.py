import pathlib
from os import makedirs
from uuid import UUID

from fastapi import UploadFile


class DownloadFiles:
    async def __call__(self, file: UploadFile, workplace_id: UUID) -> dict:
        async def download_file(file: UploadFile, workplace_id: UUID) -> dict:
            local_storage = pathlib.Path(__file__).parent.parent.parent.resolve()

            main_download_folder = local_storage.joinpath(pathlib.Path("assets"))
            workplace_download_folder = main_download_folder.joinpath(pathlib.Path(f"{workplace_id}"))
            makedirs(main_download_folder, exist_ok=True)
            makedirs(workplace_download_folder, exist_ok=True)

            photo_path = workplace_download_folder.joinpath(pathlib.Path(f"{file.filename}"))

            with open(photo_path, "wb+") as file_object:
                file_object.write(file.file.read())

            return file.filename

        return await download_file(file, workplace_id)


downloader = DownloadFiles()
