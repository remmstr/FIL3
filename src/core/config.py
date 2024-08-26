# Built-in modules
import re
import sys
from string     import ascii_lowercase, ascii_uppercase
from pathlib    import Path
from typing     import Tuple
import sys
sys.path.append('C:\\Users\\remim\\AppData\\Roaming\\Python\\Python310\\site-packages')
# Requirements modules
from customtkinter import set_default_color_theme

# Internal modules
from core.resource_manager  import ResourceHandler

class ApplicationInfo():
    title: str
    version: Tuple[int, int, int]
    icon: Path

    def __init__(self, title: str = 'Python Application', version: Tuple[int, int, int] = (0, 0, 0), log_level: int | str = 'info'):
        self.set_title(title)
        self.set_version(version[0], version[1], version[2])
        self.retrieve_icon()

    @classmethod
    def set_title(cls, value):
        cls.title = value

    @classmethod
    def set_version(cls, major: int, minor: int, patch: int):
        cls.version = (major, minor, patch)

    @classmethod
    def retrieve_icon(cls):
        root = "release/" if not cls.is_bundled() else ""
        os = sys.platform if not cls.is_bundled() else ""
        ext = "icns" if sys.platform == 'darwin' else 'ico'

        # Construct the path of the icon
        path = "{root}{os}/appicon.{ext}".format(root=root, os=os, ext=ext)

        cls.icon = ResourceHandler(path).filepath

    @staticmethod
    def is_bundled() -> bool:
        """Return `True` if the program is bundled into an executable."""
        try:
            sys._MEIPASS
        except AttributeError:
            return False
        return True

class ApplicationSettings():
    def __init__(self, theme_file: str) -> None:
        self.set_theme(theme_file)

    @staticmethod
    def set_theme(filepath: str):
        set_default_color_theme(ResourceHandler(filepath).filepath)

class KeyboardSettings():
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