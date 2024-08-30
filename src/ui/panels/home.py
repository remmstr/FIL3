# Internal modules
from core.config import LoggerSettings
from ui.utils import CTkLoggingHandler
from ui.widgets.panel import ButtonHeader, PanelTemplate
from ui.widgets.table import TableOfCasques
from ui.panels import LogConsole

# Requirements modules
from customtkinter import (
    CTkOptionMenu,
    CTkFrame
)

# Built-in modules
import logging


class Home(PanelTemplate):
    def __init__(self, parent, title) -> None:
        # Initialize inherited class
        super().__init__(
            parent=parent,
            title=title,
            fg_color=('#CCD7E0', '#313B47')
        )

        self.main_frame = CTkFrame(self, fg_color=('#E7EBEF', '#293138'), corner_radius=4)
        self.main_frame.pack(anchor='nw', expand=True, fill='both', side='top', padx=6, pady=8)

        # Set the Table for the list of casques
        self.TableOfCasques = TableOfCasques(self.main_frame)
        self.TableOfCasques.pack(anchor='nw', side='top', fill='both', padx=4, pady=8)

        # Create a separate frame for the console at the bottom
        self.console_frame = CTkFrame(self.main_frame, fg_color=('#E7EBEF', '#293138'), corner_radius=4)
        self.console_frame.pack(anchor='sw', expand=False, side='bottom', fill='x', padx=4, pady=8)

        self.console = LogConsole(self.console_frame, 'Console') 
        self.console.pack(anchor='sw', expand=True, fill='both', padx=4, pady=8)

        # Add lines to TableOfCasques
        self.TableOfCasques.add_line(tab_name='Casque 1', icon_name='biblio', default=True)
        self.TableOfCasques.add_line(tab_name='Casque 2', icon_name='biblio', default=True)
        self.TableOfCasques.add_line(tab_name='Casque 3', icon_name='biblio', default=True)
