import logging
import os.path
from io import BytesIO
from typing import BinaryIO

import PIL.Image
import aiogram.exceptions
from aiogram import Bot
from aiogram.types import StickerSet, InputSticker, FSInputFile, BufferedInputFile, URLInputFile, Sticker

from sticker_pack import media_editor
import utils
from settings import *

logger = logging.getLogger(__name__)


def is_dummy_sticker(first_sticker_file: BinaryIO) -> bool:
    try:
        with PIL.Image.open(first_sticker_file) as first_sticker_image:
            if first_sticker_image.size != (1, 512):
                return False

            for y in range(0, 512):
                if first_sticker_image.getpixel([0, y]) != (255, 255, 255):
                    return False
            return True
    except Exception:
        return False


class StickerPackEditor:
    def __init__(self, bot: Bot, user_id: int, sticker_pack_address: str):
        self.bot = bot
        self.user_id = user_id
        self.sticker_pack_address = sticker_pack_address
        self.sticker_pack: StickerSet | None = None

    @staticmethod
    async def create_new(bot: Bot, pack_data):
        from storage import PackCreationData
        pack_data: PackCreationData

        editor = StickerPackEditor(bot, pack_data.user_id, sticker_pack_address=pack_data.address)
        dummy_sticker = await editor.upload_sticker(DUMMY_STICKER_PATH)
        success = await bot.create_new_sticker_set(
            user_id=pack_data.user_id,
            name=pack_data.address,
            title=pack_data.title,
            stickers=[dummy_sticker]
        )

        if not success:
            await bot.send_message(pack_data.user_id, text="Something went wrong...")
            return
        return editor

    @staticmethod
    async def exists(bot: Bot, sticker_pack_address: str) -> bool:
        try:
            await bot.get_sticker_set(sticker_pack_address)
        except aiogram.exceptions.TelegramBadRequest:
            return False
        else:
            return True

    def get_link(self):
        return f"https://t.me/addstickers/{self.sticker_pack_address}"

    async def change_title(self, new_title: str) -> bool:
        """Returns True on success"""
        return await self.bot.set_sticker_set_title(self.sticker_pack_address, new_title)

    async def upload_sticker(self, input_data: bytes | str, emoji_list: list[str] | None = None) -> InputSticker | None:
        """Uploads given bytes, url or path to file to telegram server"""
        # TODO: handle frame_type is None
        bot = self.bot
        user_id = self.user_id

        if emoji_list is None:
            emoji_list = ["👍"]

        # download file
        if isinstance(input_data, bytes):
            # do nothing lol
            pass
        elif isinstance(input_data, str):
            if utils.is_url(input_data):
                input_data = (await utils.download_to_memory(bot, URLInputFile(input_data))).read()
            else:
                if not os.path.exists(input_data):
                    logger.error("Got not existing file.")
                    return

                input_data = (await utils.download_to_memory(bot, FSInputFile(input_data))).read()
        else:
            logger.error(f"Got unexpected type of input_data: {type(input_data)}")
            return

        # prepare media
        if media_editor.is_image_supported(input_data):
            input_data = media_editor.resize_image(input_data)
            sticker_format = "static"
            extension = "png"
        elif media_editor.is_video_supported(input_data):
            input_data = media_editor.resize_video(input_data)
            sticker_format = "video"
            extension = "webm"
        else:
            logger.error("Got unsupported media.")
            return
        filename = utils.generate_random_filename() + "." + extension

        input_file = BufferedInputFile(input_data, filename=filename)

        return InputSticker(
            sticker=(await bot.upload_sticker_file(
                user_id=user_id,
                sticker=input_file,
                sticker_format=sticker_format
            )).file_id,
            format=sticker_format,
            emoji_list=emoji_list
        )

    async def add_sticker(self, sticker: InputSticker) -> Sticker:
        """Returns True on success"""

        bot = self.bot
        user_id = self.user_id

        await self.fetch_sticker_set()
        sticker_pack = self.sticker_pack

        await bot.add_sticker_to_set(user_id, self.sticker_pack_address, sticker)
        if len(sticker_pack.stickers) == 2:
            first_sticker_file = await bot.download(sticker_pack.stickers[0].file_id, BytesIO())
            if is_dummy_sticker(first_sticker_file):
                await bot.delete_sticker_from_set(sticker_pack.stickers[0].file_id)
        await self.fetch_sticker_set()
        return sticker_pack.stickers[-1]

    async def fetch_sticker_set(self):
        if self.sticker_pack is not None:
            return

        self.sticker_pack = await self.bot.get_sticker_set(self.sticker_pack_address)

    async def delete_pack(self):
        from sticker_pack import database

        """Returns True if success"""

        success = await self.bot.delete_sticker_set(self.sticker_pack_address)
        if not success:
            return False

        database.remove_editor(self)
        return True
