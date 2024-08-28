# Requirements modules
from customtkinter import (
    CTkToplevel
    )


class PopupWindow(CTkToplevel):
    """
    Template for a child window of the main app
    """

    def __init__(self, win_title: str, win_size: tuple, *args, **kw):
        # Initialize inherited class
        super().__init__(*args, **kw)

        self.title(win_title)
        self.geometry(f'{win_size[0]}x{win_size[1]}')

    @property
    def center_coordinates(self):
        """
        Return the coordinates `[x, y]` for centering the window on the screen.
        For tkinter, we use the top-left position for setting the window.
        """

        pos_topleft = (
            int(round((self.screensize[0]/2) - (self.win_size[0]/2), 1)),
            int(round((self.screensize[1]/2) - (self.win_size[1]/2), 1)),
        )

        return pos_topleft

    @property
    def screensize(self):
        """
        Return the resolution size `[x, y]` of the screen
        """

        return (self.winfo_screenwidth(), self.winfo_screenheight())

    def close(self):
        self.destroy()