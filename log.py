import logging
from settings import LOGGING_FORMAT


class ColorHandler(logging.StreamHandler):
    # https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
    GRAY8 = '38;5;8'
    GRAY7 = '38;5;7'
    ORANGE = '33'
    RED = '31'
    WHITE = '0'
    LEVEL_COLOR_MAP = {
        logging.DEBUG: GRAY8,
        logging.INFO: GRAY7,
        logging.WARNING: ORANGE,
        logging.ERROR: RED,
    }

    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter(fmt=LOGGING_FORMAT))

    def emit(self, record):
        csi = f'{chr(27)}['
        color = self.LEVEL_COLOR_MAP.get(record.levelno, self.WHITE)

        try:
            message = self.format(record)
            stream = self.stream
            stream.write(f'{csi}{color}m{message}{csi}m' + self.terminator)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)
