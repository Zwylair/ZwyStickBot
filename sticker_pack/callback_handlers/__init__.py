from aiogram import Dispatcher, F

from sticker_pack.callback_handlers import rename_handler, delete_pack_handler, frame_change_handler
from storage import EditorPackCallback


def setup(dp: Dispatcher):
    dp.callback_query.register(
        rename_handler.rename_handler,
        EditorPackCallback.filter(F.action == "rename")
    )
    dp.callback_query.register(
        frame_change_handler.change_frame_handler,
        EditorPackCallback.filter(F.action == "change_frame")
    )
    dp.callback_query.register(
        delete_pack_handler.delete_pack_handler,
        EditorPackCallback.filter(F.action == "delete")
    )
