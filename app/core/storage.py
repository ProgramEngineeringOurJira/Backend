import pathlib


def get_workplace_storage():
    local_storage = pathlib.Path(__file__).parent.parent.parent.resolve()
    workplace_folder = local_storage.joinpath(pathlib.Path("assets/workplaces_files"))
    return workplace_folder


def get_avatar_storage():
    storage = pathlib.Path(__file__).parent.parent.parent.resolve()
    avatar_folder = storage.joinpath(pathlib.Path("assets/avatars"))
    return avatar_folder
