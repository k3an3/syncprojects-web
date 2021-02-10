from secrets import token_hex

import os


def debug_enabled() -> bool:
    return os.getenv('DEBUG') == '1'


def gen_token() -> str:
    return token_hex(16)
