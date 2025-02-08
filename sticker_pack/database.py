import logging

from aiogram import Bot

import db
import utils
from storage import *

logger = logging.getLogger(__name__)


def get_user_sticker_packs(user_id: int) -> list[str] | None:
    with db.get_closing_cursor() as cur:
        cur.execute("SELECT (sticker_packs) FROM sticker_packs WHERE user_id=?", (user_id, ))
        sticker_packs: str = utils.process_fetchone(cur.fetchone())
    return None if sticker_packs is None else sticker_packs.split(',')


def dump_user_sticker_packs(user_id: int, sticker_packs: list[str]):
    with db.get_closing_cursor() as cur:
        if get_user_sticker_packs(user_id) is None:
            cur.execute(
                "INSERT INTO sticker_packs (user_id, sticker_packs) VALUES (?, ?)",
                (user_id, ",".join(sticker_packs))
            )
        else:
            cur.execute(
                "UPDATE sticker_packs SET sticker_packs=? WHERE user_id=?",
                (",".join(sticker_packs), user_id)
            )


def add_sticker_pack_to_user(user_id: int, sticker_pack: str):
    sticker_packs = get_user_sticker_packs(user_id)

    if sticker_packs is None:
        sticker_packs = [sticker_pack]
    else:
        sticker_packs.append(sticker_pack)

    dump_user_sticker_packs(user_id, sticker_packs)


def remove_sticker_pack_from_db(user_id: int, sticker_pack_address: str):
    sticker_packs: list[str] = get_user_sticker_packs(user_id)

    if sticker_packs is None:
        logger.error("There is no any sticker packs attached to this user!")
        return

    try:
        sticker_packs.remove(sticker_pack_address)
    except ValueError as e:
        logger.error(f"Nothing to remove! Sticker pack '{sticker_pack_address}' of uid {user_id} is not in db", exc_info=e)
    else:
        dump_user_sticker_packs(user_id, sticker_packs)


def get_editor(bot: Bot, user_id: int) -> StickerPackEditor | None:
    if user_id in PACK_EDITORS_CACHE:
        return PACK_EDITORS_CACHE[user_id]

    with db.get_closing_cursor() as cur:
        cur.execute("SELECT (selected_set_name) FROM editors WHERE user_id=?", (user_id, ))
        selected_set_name: str = utils.process_fetchone(cur.fetchone())
    return None if selected_set_name else StickerPackEditor(bot, user_id, selected_set_name)


def select_editor(editor: StickerPackEditor):
    with db.get_closing_cursor() as cur:
        cur.execute("SELECT (selected_set_name) FROM editors WHERE user_id=?", (editor.user_id, ))
        selected_set_name = cur.fetchone()

        if selected_set_name is None:
            cur.execute(
                "INSERT INTO editors (user_id, selected_set_name) VALUES (?, ?)",
                (editor.user_id, editor.sticker_pack_address)
            )
        else:
            cur.execute(
                "UPDATE editors SET selected_set_name=? WHERE user_id=?",
                (editor.sticker_pack_address, editor.user_id)
            )

    PACK_EDITORS_CACHE.update({editor.user_id: editor})
