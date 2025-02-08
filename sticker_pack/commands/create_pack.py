import logging
import re

from aiogram import Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from sticker_pack import database
from message_handler import add_message_handler
from storage import *

logger = logging.getLogger(__name__)


async def message_handler(message: Message, dummy_update: DummyUpdate):
    bot = message.bot
    chat_id = message.from_user.id

    if message.chat.type != "private":
        return

    if message.text is None:
        return

    pack_creation_data = PACK_CREATION_CACHE.get(chat_id)

    if pack_creation_data is None:
        return

    dummy_update.consume()

    if pack_creation_data.address is None:
        sticker_pack_address = message.text
        necessary_postfix = f"_by_{(await bot.get_me()).username}"
        sticker_pack_address += necessary_postfix

        if re.fullmatch("[a-zA-Z0-9_]+", sticker_pack_address) is None:
            await message.answer("This address cannot be used. Only A-z, numerals and underscores")
            return

        if len(sticker_pack_address) > 64:
            await message.answer(
                f"Address '{sticker_pack_address}' cannot be longer than 64 symbols. Try again\n\n"
                f"_The `{sticker_pack_address}` is necessary thing, without it Telegram wouldn't register pack 😞_"
            )
            return

        try:
            await bot.get_sticker_set(sticker_pack_address)
        except TelegramBadRequest:
            pass
        else:
            await message.answer("This sticker pack already exists")
            return

        pack_creation_data.address = sticker_pack_address
        await message.answer("Enter new stickerpack name:")

    elif pack_creation_data.title is None:
        sticker_pack_title = message.text

        if len(sticker_pack_title) > 64:
            await message.answer("Title cannot be longer than 64 symbols. Try again")
            return

        pack_creation_data.title = sticker_pack_title
        editor = await StickerPackEditor.create_new(bot, pack_creation_data)

        PACK_CREATION_CACHE.pop(chat_id)
        PACK_EDITORS_CACHE.update({chat_id: editor})
        database.add_sticker_pack_to_user(chat_id, pack_creation_data.address)

        await message.reply(
            f"❤\uFE0F Stickerpack [{pack_creation_data.title}](https://t.me/addstickers/{pack_creation_data.address}) was successfully created!"
        )

async def create_pack(message: Message):
    bot = message.bot
    chat_id = message.from_user.id

    if message.chat.type != "private":
        return

    PACK_CREATION_CACHE[chat_id] = PackCreationData(chat_id)

    await message.answer(
        "Enter a link for new sticker pack:\n\n"
        "_For example, this pack uses 'Animals' as short link: https://t.me/addstickers/Animals_"
    )


def setup(dp: Dispatcher):
    dp.message.register(create_pack, Command("create_pack"))
    add_message_handler(message_handler)
