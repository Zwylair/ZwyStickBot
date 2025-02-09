import logging

from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram.utils.keyboard import InlineKeyboardBuilder

from settings import FRAME_PREVIEW_IMAGE_URL
from sticker_pack import database
from storage import FrameSelectorCallback, FrameTypes

logger = logging.getLogger(__name__)


async def change_frame_handler(query: CallbackQuery):
    bot = query.bot
    chat_id = query.message.chat.id

    database.remove_user_from_added_sticker_recently(chat_id)

    selector_message = await bot.send_message(
        chat_id=chat_id,
        text="Frame is a transparent background around the sticker. Choose wanted frame type:",
        link_preview_options=LinkPreviewOptions(url=FRAME_PREVIEW_IMAGE_URL)
    )

    markup_builder = InlineKeyboardBuilder()
    markup_builder.max_width = 2
    markup_builder.button(text="Lite", callback_data=FrameSelectorCallback(frame_type=FrameTypes.LITE, cancel=False, selector_message_id=selector_message.message_id))
    markup_builder.button(text="Medium", callback_data=FrameSelectorCallback(frame_type=FrameTypes.MEDIUM, cancel=False, selector_message_id=selector_message.message_id))
    markup_builder.button(text="Rounded", callback_data=FrameSelectorCallback(frame_type=FrameTypes.ROUNDED, cancel=False, selector_message_id=selector_message.message_id))
    markup_builder.button(text="Square", callback_data=FrameSelectorCallback(frame_type=FrameTypes.SQUARE, cancel=False, selector_message_id=selector_message.message_id))
    markup_builder.button(text="Circle", callback_data=FrameSelectorCallback(frame_type=FrameTypes.CIRCLE, cancel=False, selector_message_id=selector_message.message_id))
    markup_builder.button(text="❌ Cancel", callback_data=FrameSelectorCallback(frame_type=0, cancel=True, selector_message_id=selector_message.message_id))

    await query.answer()
    await selector_message.edit_reply_markup(reply_markup=markup_builder.as_markup())


async def cancel_change_frame_handler(query: CallbackQuery):
    bot = query.bot
    chat_id = query.message.chat.id
    selector_message_id = FrameSelectorCallback.unpack(query.data).selector_message_id

    database.remove_user_from_added_sticker_recently(chat_id)

    await query.answer()
    await bot.edit_message_text(chat_id=chat_id, message_id=selector_message_id, text="Frame changing canceled.")


async def frame_selector_handler(query: CallbackQuery):
    bot = query.bot
    chat_id = query.message.chat.id
    callback_data = FrameSelectorCallback.unpack(query.data)
    editor = database.get_editor(bot, chat_id)

    database.remove_user_from_added_sticker_recently(chat_id)
    database.dump_sticker_pack_frame_type(editor.sticker_pack_address, callback_data.frame_type)

    await query.answer()
    await bot.edit_message_text(chat_id=chat_id, message_id=callback_data.selector_message_id, text="Frame type was successfully changed.")
