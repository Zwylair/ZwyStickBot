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

    # TODO: maybe someday remove the limit of 9 displayed packs
    sticker_packs = database.get_user_sticker_packs(chat_id)[:9]

    markup_builder = InlineKeyboardBuilder()
    markup_builder.max_width = 1

    for sticker_pack_address in sticker_packs:
        sticker_set = await bot.get_sticker_set(sticker_pack_address)
        callback_data = SelectPackCallback(sticker_pack=sticker_pack_address, reply_to=message.message_id)
        markup_builder.button(text=sticker_set.title, callback_data=callback_data)

    await message.reply(
        "First of all, you have to choose pack for editing:",
        reply_markup=markup_builder.as_markup()
    )


async def send_sticker_pack_menu(query: CallbackQuery, editor: StickerPackEditor):
    await editor.fetch_sticker_set()

    delete_emoji = "💔" if random.randint(1, 10) <= 9 else "😔"
    markup_builder = InlineKeyboardBuilder()
    markup_builder.max_width = 1
    markup_builder.button(text="🌟 Use pack", url=editor.get_link())
    markup_builder.button(text="✏️ Rename", callback_data=EditorPackCallback(action="rename", sticker_pack=editor.sticker_pack_address))
    markup_builder.button(text="🔳 Change frame", callback_data=EditorPackCallback(action="change_frame", sticker_pack=editor.sticker_pack_address))
    markup_builder.button(text=delete_emoji + " Delete pack", callback_data=EditorPackCallback(action="delete", sticker_pack=editor.sticker_pack_address))

    await query.answer()
    await query.message.reply(
        text=f"🔆 Selected [{editor.sticker_pack.title}]({editor.get_link()}) pack!\n\n"
             "*❇️ How to add stickers?*\n"
             "> Send photo, video or sticker to add to the pack",
        reply_markup=markup_builder.as_markup(),
        disable_web_page_preview=True
    )
