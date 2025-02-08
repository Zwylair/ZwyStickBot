import logging

from aiogram import Bot
from aiogram.types import StickerSet, InputSticker, FSInputFile

from settings import *

logger = logging.getLogger(__name__)


class StickerPackEditor:
    def __init__(self, bot: Bot, user_id: int, sticker_pack_address: str, sticker_pack: StickerSet | None = None):
        self.bot = bot
        self.user_id = user_id
        self.sticker_pack_address = sticker_pack_address
        self.sticker_pack = sticker_pack

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

    def get_link(self):
        return f"https://t.me/addstickers/{self.sticker_pack_address}"

    async def add_sticker(self):
        ...
        # dummy handle

    async def fetch_sticker_set(self):
        self.sticker_pack = await self.bot.get_sticker_set(self.sticker_pack_address)
