from dataclasses import dataclass

from aiogram.filters.callback_data import CallbackData

from sticker_pack.editor import StickerPackEditor


@dataclass
class DummyUpdate:
    consumed: bool = False

    def consume(self):
        self.consumed = True


@dataclass
class PackCreationData:
    user_id: int
    title: str | None = None
    address: str | None = None


class SelectPackCallback(CallbackData, prefix="selector"):
    sticker_pack: str
    reply_to: int


class EditorPackCallback(CallbackData, prefix="editor"):
    action: str
    sticker_pack: str


PACK_CREATION_CACHE: dict[int, PackCreationData] = {}
PACK_EDITORS_CACHE: dict[int, StickerPackEditor] = {}
