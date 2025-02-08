import logging

from aiogram.types import CallbackQuery

from storage import EditorPackCallback

logger = logging.getLogger(__name__)


async def rename_handler(query: CallbackQuery):
    bot = query.bot
    chat_id = query.message.chat.id
    callback_data = EditorPackCallback.unpack(query.data)
    sticker_pack_address = callback_data.sticker_pack

    logger.info("rename handler")
