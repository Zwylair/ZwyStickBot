from aiogram import Dispatcher
from aiogram.filters import Command

import sticker_pack.commands.create_pack
from message_handler import add_message_handler


def setup(dp: Dispatcher):
    dp.message.register(create_pack.create_pack, Command("create_pack"))
    add_message_handler(create_pack.message_handler)
