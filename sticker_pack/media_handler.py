import logging

from aiogram.types import Message

import utils
from sticker_pack import database
from sticker_pack.select_pack import send_pack_selector
from storage import *

logger = logging.getLogger(__name__)


async def message_handler(message: Message, dummy_update: DummyUpdate):
    """Handles stickers, gifs, videos, images and makes stickers out of it"""
    bot = message.bot
    chat_id = message.chat.id

    if message.chat.type != "private":
        return

    if not utils.is_str_empty(message.text):
        return

    dummy_update.consume()

    editor = database.get_editor(bot, chat_id)
    if editor is None:
        await send_pack_selector(message)
