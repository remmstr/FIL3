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


class TableOfCasques(CTkFrame):
    """
    Module that create the table of casques :
    - A header at the top that can hold an image OR a text
    - A menu with a vertical list of tab
    - A footer that is configurable
    """

    def __init__(self, parent, title: str | None = None, image_name: str | None = None):
        """
        Create a new Table widget

        Parameters
        ----------
        parent : Any
            The parent widget to be set
        title : `str`, optional
            Set the title to display, by default is None
        image_name : `str`, optional
            Set the image to display. Use the name of the file without the extension, by default is None
        """
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

        # Initialize inherited class
        super().__init__(parent)

        # Initialize instance variable
        self.tabs = {}
        self.selected = None


        # Set the frame for the tab list of casques
        self.menu = CTkFrame(self)
        self.menu.configure(fg_color='transparent', corner_radius=0)
        self.menu.pack(side='top', fill='both')

        # Set the frame for the footer
        self.footer = CTkFrame(self)
        self.footer.configure(fg_color='transparent', corner_radius=0)
        self.footer.pack(side='bottom', fill='both')

    def set_header(self, title: str | None = None, image_name: str | None = None):
        """
        Set an image OR a title in the header (can't be both, the icon will be prioritized)

        Parameters
        ----------
        title : `str`, optional
            Set the title to display
        icon : `str`, optional
            Set the image to display. Use the name of the file without the extension, by default is None
        """
        if image_name is not None:
            txt = ''
            img = ImageLibrary.get_image_tkinter(image_name)
        else:
            txt = title
            img = None

        self.header = CTkLabel(
            self,
            text=txt,
            image=img,
            fg_color='transparent',
            font=('', 20, 'bold'),
            corner_radius=0
            )

    def show_header(self):
        """
        Shows the header containing the brand
        """
        self.header.pack(side='top', fill='both')

    def hide_header(self):
        """
        Hides the header containing the brand
        """
        self.header.pack_forget()

    def add_line(self, tab_name: str, icon_name: str, default: bool = False):
        """
        Add a new tab to the sidebar

        Parameters
        ----------
        ctkObject : `Any`
            Reference of the Tkinter object instance that should be controlled by the tab
        tab_name : `str`
            Set the name of the tab
        icon_name : `str`
            Set the icon of the tab. Use the name of the file without the extension
        default : `bool`, optional
            If you want this tab to be opened at the start of the application, set this parameter to `True`
        """

        # Set the title of the header

        self.tabs.update({tab_name: Line(self.menu, tab_name, icon_name)})
        self.tabs[tab_name].pack(anchor='ne', side='top', expand=True, fill='x', padx=6, pady=3)


    


class Line(CTkLabel):
    """
    Custom button for the tabs in the sidebar
    """

    def __init__(self, parent, tab_name: str, icon_name: str):
        """
        Create a new tab for the sidebar

        Parameters
        ----------
        parent : `Any`
            The parent widget to be set
        ctkObject : `Any`
            Reference of the Tkinter object instance that should be controlled by the tab
        tab_name : `str`
            Set the title to display
        icon_name : `str`
            Set the image to display. Use the name of the file without the extension
        """
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

        # Initialize inherited class
        super().__init__(parent)
        self.configure(
            text=tab_name,
            #font=FontLibrary.get_font_tkinter('Inter 18pt', 'SemiBold', 14),
            #image=IconLibrary.get_icon_tkinter(icon_name, size=(20, 20)),
            #fg_color='transparent',
            #corner_radius=4,
            #border_width=0,
            #border_spacing=6,
            #width=24,
            anchor='w'
        )

        # Initialize instance variable
        self.tab_name = tab_name
