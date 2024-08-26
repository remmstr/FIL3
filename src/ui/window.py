# Built-in modules
import logging
from typing import Tuple
from tkinter import PhotoImage

# Requirements modules
from customtkinter import (
    CTk,
    CTkFrame,
    CTkLabel,
    CTkProgressBar
)

# Internal modules
from core.config            import ApplicationInfo
from ui.widgets             import Sidebar, PopupWindow
from ui.panels              import LogConsole
from ui.panels              import GestionDesCasques

#~~~~~ MAIN ~~~~~#

class MainWindow(CTk):
    def __init__(self, win_size: Tuple[int, int] = (1366, 768)):
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))
        self.log.info('Initializing main window')

        # Initialize instance variable
        self.win_size = win_size

        # Initialize inherited class
        super().__init__()
        self.title(ApplicationInfo.title)
        self.geometry(f'+{self.center_coordinates[0]}+{self.center_coordinates[1]}') # Center the window to the screen
        self.minsize(win_size[0], win_size[1])
        #self.iconphoto(False, PhotoImage(file=str(ApplicationInfo.icon))) # Use this to set the icon on the taskbar of the OS.
        
        # Set control bindings when app is exiting
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.bind('<Control-q>', self.quit)

        # Set the sidebar for the tabs
        self.sidebar = Sidebar(self)
        self.sidebar.pack(anchor='nw', fill='y', side='left', padx=4, pady=8)

        # Set the main container for the layouts
        self.main_frame = CTkFrame(self, fg_color=('#E7EBEF', '#293138'), corner_radius=4)
        self.main_frame.pack(anchor='nw', expand=True, fill='both', side='left', padx=6, pady=8)

        # Set the layouts and tabs
        self.layout_home = GestionDesCasques(self.main_frame, '')
        self.sidebar.add_tab(self.layout_home, name='Gestion des casques', icon='home')

        self.layout_console = LogConsole(self.main_frame, 'Logs') # Calling the widget to link it to the main_frame
        self.sidebar.add_tab(self.layout_console, name='Logs', icon='terminal', default=True) # Using the add_tab function to load it into the sidebar, and voilà!

        self.layout_setting = CTkFrame(self.main_frame, fg_color=('#CCD7E0', '#313B47'))
        self.sidebar.add_tab(self.layout_setting, name='Settings', icon='settings')

    def quit(self, *args):
        self.destroy()

    @property
    def center_coordinates(self):
        """
        Return the coordinates `[x, y]` for centering the window on the screen.
        For tkinter, we use the top-left position for setting the window.
        """

        pos_topleft = [
            int(round((self.screensize[0]/2) - (self.win_size[0]/2), 1)),
            int(round((self.screensize[1]/2) - (self.win_size[1]/2), 1)),
        ]

        return pos_topleft

    @property
    def screensize(self):
        """Return the resolution size `[x, y]` of the screen."""
        return [self.winfo_screenwidth(), self.winfo_screenheight()]

#~~~~~ POP-UP ~~~~~#

class LoadingPopup(PopupWindow):
    """
    Simple little window that show a loading bar.
    Just a little boilerplate, nothing finished.
    """

    def __init__(self, text: str, *args, **kw):
        # Initialize inherited class
        super().__init__(text, (256, 128), *args, **kw)
        self.text = text

        self.header = CTkLabel(self, text=text)
        self.header.pack(pady=20)

        self.progress = CTkProgressBar(self, orient="horizontal", length=100, mode="indeterminate")
        self.progress.pack(pady=10)
        self.progress.start()