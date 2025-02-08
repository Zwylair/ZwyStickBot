import logging

from aiogram.types import CallbackQuery

from storage import EditorPackCallback

logger = logging.getLogger(__name__)


async def delete_pack_handler(query: CallbackQuery):
    bot = query.bot
    chat_id = query.message.chat.id

    logger.info("delete_pack_handler")
