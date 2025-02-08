import logging

from aiogram.types import CallbackQuery, Message

from sticker_pack import database
from storage import DummyUpdate

logger = logging.getLogger(__name__)


async def message_handler(message: Message, dummy_update: DummyUpdate):
    bot = message.bot
    chat_id = message.chat.id
    sticker_pack_title = message.text

    if not database.is_user_waiting_for_rename(chat_id):
        return

    dummy_update.consume()

    if len(sticker_pack_title) > 64:
        await message.answer("Title cannot be longer than 64 symbols. Try again")
        return

    editor = database.get_editor(bot, chat_id)
    await editor.change_title(sticker_pack_title)
    database.remove_user_from_waiting_for_rename(chat_id)

    await message.reply(
        f"❤\uFE0F Stickerpack [{sticker_pack_title}](https://t.me/addstickers/{editor.sticker_pack_address}) was successfully renamed!"
    )


async def rename_handler(query: CallbackQuery):
    bot = query.bot
    chat_id = query.message.chat.id

    await query.answer()
    await bot.send_message(chat_id, text="Send new title for your sticker pack:")
    database.add_user_to_waiting_for_rename(chat_id)
