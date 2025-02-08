import logging
from typing import Callable, Any

from aiogram import Dispatcher
from aiogram.types import Message

from storage import DummyUpdate

logger = logging.getLogger(__name__)


async def message_handler(message: Message):
    update = DummyUpdate()

    for handler in _message_handlers:
        logger.info(f"Handling message via {handler.__module__}.{handler.__name__}")
        await handler(message, update)

        if update.consumed:
            logger.info(f"Update was consumed.")
            break
    else:
        logger.info(f"Well, update was not consumed at all. idk bruh")

def add_message_handler(handler: Callable[[Message, DummyUpdate], Any]):
    _message_handlers.append(handler)


def setup(dp: Dispatcher):
    dp.message.register(message_handler)


_message_handlers: list[Callable[[Message, DummyUpdate], Any]] = []
