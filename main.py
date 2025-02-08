import os
import asyncio
import logging

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.methods import DeleteWebhook

import db
import sticker_pack
import message_handler
from log import ColorHandler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, handlers=[ColorHandler()])

dotenv.load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()


async def main():
    db.init()
    with db.get_closing_cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sticker_packs (
                user_id INT,
                sticker_packs TEXT
            )
            """.strip()
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS editors (
                user_id INT,
                selected_set_name TEXT
            )
            """.strip()
        )

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

    sticker_pack.setup(dp)
    message_handler.setup(dp)  # message handlers should be registered after anything else
    await bot(DeleteWebhook(drop_pending_updates=True))  # skip updates
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
