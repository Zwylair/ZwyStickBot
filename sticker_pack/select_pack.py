import logging
import random

from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from storage import *
from sticker_pack import database
from storage import SelectPackCallback

logger = logging.getLogger(__name__)


async def choose_pack_inline_callback_handler(query: CallbackQuery):
    bot = query.bot
    chat_id = query.message.chat.id
    callback_data = SelectPackCallback.unpack(query.data)

    editor = StickerPackEditor(bot, chat_id, callback_data.sticker_pack)
    database.select_editor(editor)
    await send_sticker_pack_menu(query, editor)


async def send_pack_selector(message: Message):
    bot = message.bot
    chat_id = message.from_user.id

    database.remove_user_from_added_sticker_recently(chat_id)

    # TODO: maybe someday remove the limit of 9 displayed packs
    sticker_packs = database.get_user_sticker_packs(chat_id)[:9]

    markup_builder = InlineKeyboardBuilder()
    markup_builder.max_width = 1

    for sticker_pack_address in sticker_packs:
        if not await StickerPackEditor.exists(bot, sticker_pack_address):
            database.remove_sticker_pack_from_db(chat_id, sticker_pack_address)
            continue

        sticker_set = await bot.get_sticker_set(sticker_pack_address)
        callback_data = SelectPackCallback(sticker_pack=sticker_pack_address, reply_to=message.message_id)
        markup_builder.button(text=sticker_set.title, callback_data=callback_data)

    await message.reply(
        text="First of all, you have to choose pack for editing:",
        reply_markup=markup_builder.as_markup()
    )


async def send_sticker_pack_menu(query: CallbackQuery, editor: StickerPackEditor):
    database.remove_user_from_added_sticker_recently(query.message.chat.id)
    await editor.fetch_sticker_set()

    delete_emoji = "💔" if random.randint(1, 10) <= 9 else "😔"
    markup_builder = InlineKeyboardBuilder()
    markup_builder.max_width = 1
    markup_builder.button(text="🌟 Use pack", url=editor.get_link())
    markup_builder.button(text="✏️ Rename", callback_data=EditorPackCallback(action="rename"))
    markup_builder.button(text="🔳 Change frame", callback_data=EditorPackCallback(action="change_frame"))
    markup_builder.button(text=delete_emoji + " Delete pack", callback_data=EditorPackCallback(action="delete"))

    await query.answer()
    await query.message.reply(
        text=f"🔆 Selected [{editor.sticker_pack.title}]({editor.get_link()}) pack!\n\n"
             "*❇️ How to add stickers?*\n"
             "> Send photo, video or sticker to add to the pack",
        reply_markup=markup_builder.as_markup(),
        disable_web_page_preview=True
    )
