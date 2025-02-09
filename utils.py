import io
import random
import string

import emoji
from aiogram import Bot
from aiogram.types import URLInputFile, FSInputFile


def is_str_empty(variable: str):
    return variable is None or len(variable) == 0


def process_fetchone(fetching_result):
    return None if fetching_result is None else next(iter(fetching_result), None)


def is_url(variable: str) -> bool:
    return variable.startswith("https://") or variable.startswith("http://")


def generate_random_filename(length: int = 8) -> str:
    return "".join([random.choice(string.hexdigits) for _ in range(length)])


async def download_to_memory(bot: Bot, file: URLInputFile | FSInputFile) -> io.BytesIO:
    buffer = io.BytesIO()

    async for chunk in file.read(bot):
        buffer.write(chunk)

    buffer.seek(0)
    return buffer


def split_emojis(text: str):
    return [e["emoji"] for e in emoji.emoji_list(text)]