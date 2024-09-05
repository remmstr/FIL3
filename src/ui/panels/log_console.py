# Internal modules
from core.config import LoggerSettings
from ui.utils import CTkLoggingHandler
from ui.widgets.panel import ButtonHeader, PanelTemplate
from ui.widgets.console import ConsoleStream

# Requirements modules
from customtkinter import (
    CTkOptionMenu
)

# Built-in modules
import logging


class LogConsole(PanelTemplate):
    def __init__(self, parent, title) -> None:
        # Initialize inherited class
        super().__init__(
            parent=parent,
            title=title,
            fg_color=('#CCD7E0', '#313B47')
        )

        self.console = ConsoleStream(self)
        self.console.pack(anchor='nw', expand=True, fill='both', side='top', padx=8)

        # Set the handler for the logger with the custom CTkHandler
        self.log_handler = CTkLoggingHandler(self.console, LoggerSettings.log_level)
        self.log_handler.setFormatter(logging.Formatter('\x1b[36m[%(levelname)s]\x1b[0m \x1b[37m[%(name)s]\x1b[0m %(message)s'))
        self.log.root.addHandler(self.log_handler)

        #self.selectbox = CTkOptionMenu(self.header.widgets_frame, values=['Log1', 'Log2', 'Log3'], command=self.select_interpreter)
        #self.selectbox.pack(anchor='e', side='left', padx=4)

        #self.button_clear = ButtonHeader(self.header.widgets_frame, tooltip='Clear console', icon_name='eraser', command=self.console.clear)
        #self.button_clear.pack(anchor='e', side='left')

        #self.select_interpreter('Log1')

    #def select_interpreter(self, choice):
        #self.log.info('Changing stream for {}'.format(choice))