import pathlib
from os import makedirs

from fastapi import UploadFile


class DownloadFiles:
    async def __call__(self, file: UploadFile) -> dict:
        async def download_file(file: UploadFile) -> dict:
            local_storage = pathlib.Path(__file__).parent.parent.parent.resolve()
            folder_where_to_download = local_storage.joinpath(pathlib.Path("my_files"))
            photo_path = folder_where_to_download.joinpath(pathlib.Path(f"{file.filename}"))

            makedirs(folder_where_to_download, exist_ok=True)
            with open(photo_path, "wb+") as file_object:
                file_object.write(file.file.read())

            return file.filename

        return await download_file(file)


downloader = DownloadFiles()
