import random
import logging

from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sticker_pack import database
from storage import DeletePackCallback

logger = logging.getLogger(__name__)


async def delete_pack_handler(query: CallbackQuery):
    bot = query.bot
    chat_id = query.message.chat.id

    database.remove_user_from_added_sticker_recently(chat_id)

    delete_propose_message = await bot.send_message(chat_id, text=f"Are you sure you wanna delete this pack?")

    markup_builder = InlineKeyboardBuilder()
    markup_builder.max_width = 1
    buttons = [
        InlineKeyboardButton(
            text="Eww... Maybe not",
            callback_data=DeletePackCallback(
                action="cancel_delete",
                delete_propose_message_id=delete_propose_message.message_id
            ).pack()
        ),
        InlineKeyboardButton(
            text="Nah",
            callback_data=DeletePackCallback(
                action="cancel_delete",
                delete_propose_message_id=delete_propose_message.message_id
            ).pack()
        ),
        InlineKeyboardButton(
            text="Yeah, I'm sure",
            callback_data=DeletePackCallback(
                action="im_sure_to_delete",
                delete_propose_message_id=delete_propose_message.message_id
            ).pack()
        )
    ]
    random.shuffle(buttons)
    markup_builder.add(*buttons)

    await query.answer()
    await delete_propose_message.edit_reply_markup(reply_markup=markup_builder.as_markup())


async def cancel_delete_pack_handler(query: CallbackQuery):
    bot = query.bot
    chat_id = query.message.chat.id
    delete_propose_message_id = DeletePackCallback.unpack(query.data).delete_propose_message_id

    database.remove_user_from_added_sticker_recently(chat_id)

    await query.answer()
    await bot.edit_message_text(chat_id=chat_id, message_id=delete_propose_message_id, text="Pack deletion canceled.")


async def second_delete_pack_handler(query: CallbackQuery):
    bot = query.bot
    chat_id = query.message.chat.id
    delete_propose_message_id = DeletePackCallback.unpack(query.data).delete_propose_message_id
    editor = database.get_editor(bot, chat_id)

    database.remove_user_from_added_sticker_recently(chat_id)

    if editor is None:
        await query.answer()
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=delete_propose_message_id,
            text="This sticker pack is already deleted.",
        )
        return

    await editor.fetch_sticker_set()
    success = await editor.delete_pack()
    await query.answer()

    if success:
        database.remove_sticker_pack_from_db(chat_id, editor.sticker_pack_address)
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=delete_propose_message_id,
            text=f"Sticker pack [{editor.sticker_pack.title}]({editor.get_link()}) was deleted.",
            disable_web_page_preview=True
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="Something went wrong..."
        )
