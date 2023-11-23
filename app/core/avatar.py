import pathlib
from hashlib import md5
from os import makedirs
from typing import List

from numpy import array, concatenate
from PIL import Image, ImageDraw

from app.config import avatar_settings
from app.core.exceptions import AvatarSizeNotCorrectException


class Avatar:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Avatar, cls).__new__(cls)
        return cls.instance

    background_color: str = avatar_settings.BACKGROUND_COLOR

    avatar_size = avatar_settings.AVATAR_SIZE

    async def generate_avatar(self, user_name: str) -> List[List[bool]]:
        bytes = md5(user_name.encode("utf-8")).digest()

        need_color = array([bit == "1" for byte in bytes[3 : 3 + 9] for bit in bin(byte)[2:].zfill(8)]).reshape(6, 12)
        need_color = concatenate((need_color, need_color[::-1]), axis=0)

        for i in range(12):
            need_color[0, i] = 0
            need_color[11, i] = 0
            need_color[i, 0] = 0
            need_color[i, 11] = 0

        main_color = bytes[:3]
        main_color = tuple(channel // 2 + 128 for channel in main_color)

        if self.avatar_size % 12 != 0:
            raise AvatarSizeNotCorrectException("Avatar size must be a multiple of 12")

        img_size = (self.avatar_size, self.avatar_size)
        block_size = self.avatar_size // 12

        img = Image.new("RGB", img_size, self.background_color)
        draw = ImageDraw.Draw(img)

        for x in range(self.avatar_size):
            for y in range(self.avatar_size):
                need_to_paint = need_color[x // block_size, y // block_size]
                if need_to_paint:
                    draw.point((x, y), main_color)

        storage = pathlib.Path(__file__).parent.parent.parent.resolve()
        avatar_folder = storage.joinpath(pathlib.Path("assets/avatars"))
        makedirs(avatar_folder, exist_ok=True)

        avatar_path = avatar_folder.joinpath(pathlib.Path(user_name + ".png"))
        img.save(avatar_path, "png")


avatar = Avatar()
