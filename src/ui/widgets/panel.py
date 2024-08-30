# Internal modules
from core.resource import FontLibrary, IconLibrary

# Requirements modules
from tktooltip import ToolTip
from customtkinter import (
    CTkButton,
    CTkFrame,
    CTkLabel
    )

# Built-in modules
import logging


class PanelTemplate(CTkFrame):
    """
    Base template for a panel including a header
    """

    def __init__(self, parent, title: str, **kwargs):
        """
        Create a new panel

        Parameters
        ----------
        parent : `Any`
            The parent widget to be set.
        title : `str`
            The title that will be display on the header.
        **kwargs : 
            Any other parameters that can be used with a CTkFrame
        """
        # Set instance logger
        self.log = logging.getLogger(self.__class__.__name__)

        # Initialize inherited class
        super().__init__(parent, **kwargs)

        # Adding header
        self.header = PanelHeader(self, title=title, fg_color=self._fg_color)
        self.header.pack(anchor='nw', fill='x', side='top', padx=10, pady=8)


class PanelHeader(CTkFrame):
    """
    Template for a panel with a header that can hold widgets.\n
    The title is set to the left and widgets are put inside a frame that is placed to the left.
    """

    def __init__(self, parent, title: str, **kwargs):
        """
        Create a panel header

        Parameters
        ----------
        parent : `Any`
            The parent widget to be set.
        title : `str`
            The title that will be display on the header.
        **kwargs : 
            Any other parameters that can be used with a CTkFrame
        """
        # Initialize inherited class
        super().__init__(parent, **kwargs)
        self.configure(corner_radius=0)

        # Initialize instance variable
        self.widgets = []

        # Set the title of the header
        self.title = CTkLabel(self, text=title, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 18), anchor='w')
        self.title.pack(anchor='w', expand=True, side='left', fill='x', padx=2)

        # Set the frame for holding the different buttons
        self.widgets_frame = CTkFrame(self, height=1, fg_color='transparent')
        self.widgets_frame.pack(anchor='w', side='right')


class ButtonHeader(CTkButton):
    """
    Template for a button that can be set in a panel header.\n
    It's best to keep the same shape of button (text or icon only) for keeping a good layout.
    """
    def __init__(self, parent, text: str | None = None, tooltip: str | None = None, icon_name: str = 'home', icon_size: int = 16, **kwargs):
        """
        Create a new button.
        To be set inside a PanelHeader.

        Parameters
        ----------
        parent : `Any`
            The parent widget to be set.
        text : `str`, optional
            Set the name of the button, by default is `None`.
        tooltip : `str`, optional
            Set the text helper that can be shown when hovering the button, by default is `None`.
        icon_name : `str`, optional
            Set the icon to display. Use the name of the file without the extension, by default is `home`.
        icon_size : `int`, optional
            Set the size of the icon, by default is `16`.
        """
        # Reduce the width of the widget to the icon size if there is no text. Else return the width
        if text is None:
            width = icon_size + 4
        else:
            width = kwargs.pop('width') | 140

        # Initialize inherited class
        super().__init__(
            master=parent,
            text=text,
            image=IconLibrary.get_icon_tkinter(icon_name, size=(icon_size, icon_size)),
            width=width,
            **kwargs
            )

        # Set the tooltip if the parameter is used
        if tooltip is not None:
            ToolTip(self, msg=tooltip)

