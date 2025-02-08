import logging

import aiogram.exceptions
from aiogram import Bot
from aiogram.types import StickerSet, InputSticker, FSInputFile

from settings import *

logger = logging.getLogger(__name__)


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

        dummy_sticker = InputSticker(
            sticker=(await bot.upload_sticker_file(
                user_id=pack_data.user_id,
                sticker=FSInputFile(DUMMY_STICKER_PATH),
                sticker_format="static"
            )).file_id,
            format="static",
            emoji_list=["👍"]
        )

        success = await bot.create_new_sticker_set(
            user_id=pack_data.user_id,
            name=pack_data.address,
            title=pack_data.title,
            stickers=[dummy_sticker]
        )

        if not success:
            await bot.send_message(
                pack_data.user_id,
                "Something went wrong..."
            )

        return StickerPackEditor(
            bot,
            user_id=pack_data.user_id,
            sticker_pack_address=pack_data.address
        )

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

    async def add_sticker(self):
        """Returns True on success"""
        ...
        # dummy handle

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
