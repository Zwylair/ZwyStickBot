from aiogram import Dispatcher
from aiogram.filters import Command

from message_handler import add_message_handler
import sticker_pack.media_handler
import sticker_pack.commands
import sticker_pack.select_pack
import sticker_pack.callback_handlers
from storage import SelectPackCallback


def setup(dp: Dispatcher):
    add_message_handler(sticker_pack.media_handler.message_handler)
    add_message_handler(sticker_pack.media_handler.change_emoji_handler)
    sticker_pack.commands.setup(dp)
    sticker_pack.callback_handlers.setup(dp)
    dp.callback_query.register(
        sticker_pack.select_pack.choose_pack_inline_callback_handler,
        SelectPackCallback.filter()
    )
    dp.message.register(
        sticker_pack.select_pack.send_pack_selector,
        Command("send_selector")
    )
