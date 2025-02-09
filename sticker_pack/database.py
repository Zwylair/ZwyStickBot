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
    return None if selected_set_name is None else StickerPackEditor(bot, user_id, selected_set_name)


def remove_editor(editor: StickerPackEditor):
    if editor.user_id in PACK_EDITORS_CACHE:
        PACK_EDITORS_CACHE.pop(editor.user_id)

    with db.get_closing_cursor() as cur:
        cur.execute("DELETE FROM editors WHERE user_id=?", (editor.user_id, ))


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


def is_user_waiting_for_rename(user_id: int) -> bool:
    if user_id in USERS_WAITING_FOR_RENAME_CACHE:
        return True

    with db.get_closing_cursor() as cur:
        cur.execute("SELECT (user_id) FROM users_waiting_for_rename WHERE user_id=?", (user_id,))
        result = cur.fetchone()
    return result is not None


def add_user_to_waiting_for_rename(user_id: int):
    USERS_WAITING_FOR_RENAME_CACHE.append(user_id)

    with db.get_closing_cursor() as cur:
        cur.execute("SELECT (user_id) FROM users_waiting_for_rename WHERE user_id=?", (user_id, ))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO users_waiting_for_rename (user_id) VALUES (?)",(user_id, ))


def remove_user_from_waiting_for_rename(user_id: int):
    if user_id in USERS_WAITING_FOR_RENAME_CACHE:
        USERS_WAITING_FOR_RENAME_CACHE.remove(user_id)

    with db.get_closing_cursor() as cur:
        cur.execute("DELETE FROM users_waiting_for_rename WHERE user_id=?",(user_id, ))


def get_sticker_pack_frame_type(sticker_pack_address: str) -> int | None:
    if sticker_pack_address in STICKER_PACK_FRAME_TYPE_CACHE:
        return STICKER_PACK_FRAME_TYPE_CACHE[sticker_pack_address]

    with db.get_closing_cursor() as cur:
        cur.execute("SELECT (frame_type) FROM frame_type WHERE sticker_pack_address=?", (sticker_pack_address,))
        result = utils.process_fetchone(cur.fetchone())
    return None if result is None else result


def dump_sticker_pack_frame_type(sticker_pack_address: str, frame_type: int):
    STICKER_PACK_FRAME_TYPE_CACHE[sticker_pack_address] = frame_type

    with db.get_closing_cursor() as cur:
        cur.execute("SELECT (frame_type) FROM frame_type WHERE sticker_pack_address=?", (sticker_pack_address, ))

        if cur.fetchone() is None:
            cur.execute("INSERT INTO frame_type (sticker_pack_address, frame_type) VALUES (?, ?)",(sticker_pack_address, frame_type))
        else:
            cur.execute(
                "UPDATE frame_type SET frame_type=? WHERE sticker_pack_address=?",
                (frame_type, sticker_pack_address)
            )


def add_user_to_added_sticker_recently(user_id: int, sticker_file_id: str):
    ADDED_STICKER_RECENTLY[user_id] = sticker_file_id


def remove_user_from_added_sticker_recently(user_id: int):
    if user_id in ADDED_STICKER_RECENTLY:
        ADDED_STICKER_RECENTLY.pop(user_id)


def is_user_in_added_sticker_recently(user_id: int):
    return user_id in ADDED_STICKER_RECENTLY


def get_sticker_from_added_recently_cache(user_id: int) -> str | None:
    return ADDED_STICKER_RECENTLY.get(user_id)
