import logging
from io import BytesIO

from aiogram.types import Message, InputSticker

import utils
from sticker_pack import database
from sticker_pack.select_pack import send_pack_selector
from storage import *

logger = logging.getLogger(__name__)


async def change_emoji_handler(message: Message, dummy_update: DummyUpdate):
    bot = message.bot
    chat_id = message.chat.id

    if message.chat.type != "private":
        return

    if not database.is_user_in_added_sticker_recently(chat_id):
        return

    dummy_update.consume()

    success = await bot.set_sticker_emoji_list(database.get_sticker_from_added_recently_cache(chat_id), utils.split_emojis(message.text))
    if success:
        await message.reply(text="Emoji was successfully set to the sticker!")
        database.remove_user_from_added_sticker_recently(chat_id)
    else:
        await message.reply(text="Something went wrong when i tried to set emoji to sticker...")



async def message_handler(message: Message, dummy_update: DummyUpdate):
    """Handles stickers, gifs, videos, images and makes stickers out of it"""
    bot = message.bot
    chat_id = message.chat.id

    if message.chat.type != "private":
        return

    if not utils.is_str_empty(message.text):
        return

    dummy_update.consume()
    database.remove_user_from_added_sticker_recently(chat_id)

    editor = database.get_editor(bot, chat_id)
    if editor is None:
        await send_pack_selector(message)

    if message.sticker is not None:
        if message.sticker.is_animated:
            await message.reply(text="Animated stickers is not supported.")
            return

        input_sticker = InputSticker(
            sticker=message.sticker.file_id,
            format="video" if message.sticker.is_video else "static",
            emoji_list=[message.sticker.emoji]
        )
    elif message.photo is not None:
        file = await bot.download(message.photo[-1].file_id, BytesIO())
        input_sticker = await editor.upload_sticker(file.read())
    elif message.animation is not None:  # gif
        file = await bot.download(message.animation.file_id, BytesIO())
        input_sticker = await editor.upload_sticker(file.read())
    elif message.video is not None:
        file = await bot.download(message.video.file_id, BytesIO())
        input_sticker = await editor.upload_sticker(file.read())
    elif message.document is not None:
        file = await bot.download(message.video.file_id, BytesIO())
        input_sticker = await editor.upload_sticker(file.read())
    else:
        await message.reply(text="It doesn't seems like a media for sticker.")
        return

    added_sticker = await editor.add_sticker(input_sticker)
    database.add_user_to_added_sticker_recently(chat_id, added_sticker.file_id)
    await message.reply(
        text="*Sticker was successfully added!*\n"
             f"[\n]({editor.get_link()})"
             "\n"
             "Within an hour, this pack will be updated for all users\n"
             "\n"
             "_Send one or more emoji that I will attach to the sticker, if you want_"
    )
