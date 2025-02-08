from aiogram import Dispatcher, F

from message_handler import add_message_handler
from sticker_pack.callback_handlers import rename_handler, delete_pack_handler, frame_change_handler
from storage import EditorPackCallback, DeletePackCallback


def setup(dp: Dispatcher):
    add_message_handler(rename_handler.message_handler)
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
    dp.callback_query.register(
        delete_pack_handler.cancel_delete_pack_handler,
        DeletePackCallback.filter(F.action == "cancel_delete")
    )
    dp.callback_query.register(
        delete_pack_handler.second_delete_pack_handler,
        DeletePackCallback.filter(F.action == "im_sure_to_delete")
    )
