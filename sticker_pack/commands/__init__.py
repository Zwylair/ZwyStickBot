from aiogram import Dispatcher
import sticker_pack.commands.create_pack


def setup(dp: Dispatcher):
    create_pack.setup(dp)
