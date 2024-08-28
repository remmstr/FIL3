# Internal modules
from core.resource import ResourceHandler

# Requirements modules
from customtkinter import set_default_color_theme

# Built-in modules
import logging
from pathlib import Path
from typing import Tuple


class WindowSettings():
    """
    Base class for setting the winow states and informations.\n
    It is important to call it once before calling the MainWindow. Otherwise, the application may not launch.

    Class Variables
    -------
    title : `str`, optional
        _description_, by default is `None`
    version : `Tuple[int, int, int]`, optional
        dazd, by default is `(0, 0, 0)`
    win_icon : `Path`, optional
        , by default is `None`
    taskbar_icon : `Path`, optional
        The path to the resource of icon, by default is `None`

    Methods
    -------
    set_title : `classmethod`
        Set the title of the application
    set_version : `classmethod`
        Set the version of the application
    set_win_icon : `classmethod`
        Set the path for the icon in the window title bar. Doesn't work on MacOS.
    set_taskbar_icon : `classmethod`
        Set the path for the icon in the taskbar/dock
    set_theme : `staticmethod`
        Set the theme of the application from a json file
    """
    title: str = None
    version: Tuple[int, int, int] = None
    win_icon : Path = None
    taskbar_icon : Path = None

    def __init__(self,
                 title: str = 'Python Application',
                 version: Tuple[int, int, int] = (0, 0, 0),
                 win_icon: str | Path | None = None,
                 taskbar_icon: str | Path | None = None,
                 theme_file: str | Path | None = None):
        """
        Initialize the window settings

        Parameters
        ----------
        title : `str`, optional
            Set the title that will be shown in the main window, by default is `'Python Application'`
        version : `Tuple[int, int, int]`, optional
            Set the version of the app, by default is `(0, 0, 0)`
        win_icon : `str | Path`, optional
            Set the path of the image file to be used for the window icon, by default is `None`
        taskbar_icon : `str | Path`, optional
            Set the path of the image file to be used for the taskbar icon (or dock in MacOS), by default is `None`
        set_theme : `str | Path`, optional
            Set the path of a json file to change the color theme of the window, by default is `None`
        """
        self.set_title(title)
        self.set_version(version[0], version[1], version[2])
        self.set_win_icon(win_icon)
        self.set_taskbar_icon(taskbar_icon)
        self.set_theme(theme_file)

    @classmethod
    def set_title(cls,
                  title: str):
        """
        Set the title of the application
        """
        cls.title = title

    @classmethod
    def set_version(cls,
                    major: int = 0,
                    minor: int = 0,
                    patch: int = 0):
        """
        Set the version of the application
        """
        cls.version = (major, minor, patch)

    @classmethod
    def set_win_icon(cls,
                     filepath: str | Path | None = None):
        """
        Set the path for the icon in the window title bar.
        Doesn't work on MacOS.

        Parameters
        ----------
        filepath : `str | Path`
            Path to the file of the icon, can only take a .ico or .icns format

        Raises
        ------
        `Exception`
            The image file has not the good extension. It must be one of these formats: `.ico`, `.icns`
        """
        if filepath is not None:
            if Path(filepath).suffix in ['.icns', '.ico']:
                try:
                    cls.win_icon = ResourceHandler(filepath).resource_path
                except FileNotFoundError:
                    logging.getLogger(cls.__name__).warning("Could not find the icon file for the window")
            else:
                raise Exception("The image file for the window icon must be one of these formats: .ico, .icns")

    @classmethod
    def set_taskbar_icon(cls,
                         filepath: str | Path | None = None):
        """
        Set the path for the icon in the taskbar/dock

        Parameters
        ----------
        filepath : `str | Path`
            Path to the file of the icon, can only take a .png format

        Raises
        ------
        `Exception`
            The image file has not the good extension. It must be one of these formats: `.png`
        """
        if filepath is not None:
            if Path(filepath).suffix == '.png':
                try:
                    cls.taskbar_icon = ResourceHandler(filepath).resource_path
                except FileNotFoundError:
                    logging.getLogger(cls.__name__).warning("Could not find the icon file for the taskbar/dock")
            else:
                raise Exception("The image file for the taskbar/dock icon must be .png file")

    @staticmethod
    def set_theme(filepath: str | Path):
        """
        Set the theme of the application from a json file

        Parameters
        ----------
        filepath : `str | Path`
            The path pointing to the theme file. The file must be in a json format.
        """
        if Path(filepath).suffix == '.json':
            set_default_color_theme(ResourceHandler(filepath).resource_path)