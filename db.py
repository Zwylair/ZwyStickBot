import sqlite3
from contextlib import closing

from settings import *

CONNECTION: sqlite3.Connection


def get_conn() -> sqlite3.Connection:
    return CONNECTION


def get_cursor() -> sqlite3.Cursor:
    return CONNECTION.cursor()


def get_closing_cursor() -> closing[sqlite3.Cursor]:
    return closing(get_cursor())


def init():
    global CONNECTION
    CONNECTION = sqlite3.connect(DATABASE_PATH, autocommit=True)
