# Built-in modules
import re
import sys
from string import ascii_lowercase, ascii_uppercase


class KeyboardSettings():
    """
    Base class for setting the keyboard.
    For the moment, it's more a way of helping with GUI development than a class that can change keyboard behavior.
    """
    @staticmethod
    def get_control_state() -> int:
        """
        Give the correct control binding for TKinter.\n
        Return `4` on Windows, `8` on MacOS.
        """
        match sys.platform:
            case 'win32':
                return 4
            case 'darwin':
                return 8

    @staticmethod
    def get_regex_key_characters(regex: str) -> dict:
        """
        Give a regex list of keys to allow accelerators (keyboard shortcuts) to work if caps lock is active.
        """
        alphabet = [list(ascii_lowercase), list(ascii_uppercase)]
        key_list = {}

        for i in range(len(alphabet[0])):
            key = f'key-{alphabet[0][i]}'
            reg = f'[{alphabet[0][i]}, {alphabet[1][i]}]'
            key_list.update({key : re.compile(reg)})

        return key_list[regex]