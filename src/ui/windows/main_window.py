# Built-in modules
import logging
from typing import Tuple

# Requirements modules
from customtkinter import (
    CTk,
    CTkFrame
)

# Internal modules
from core.config import WindowSettings
from ui.widgets import Sidebar
from ui.panels import LogConsole
from ui.panels.home import Home


class MainWindow(CTk):
    """
    Main window of the application
    
    Examples
    --------
    For launching the GUI, we need to start the main loop of Tkinter. This is done directly within this class:
    >>> app = MainWindow()
    >>> app.mainloop()

    This is needed before opening child windows, as Tkinter can't work on UI object without the main loop.
    """

    def __init__(self, win_size: Tuple[int, int] = (1366, 768)):
        """
        Initialize the main window

        Parameters
        ----------
        win_size : `Tuple[int, int]`, optional
            Set the window size, by default is `(1333, 768)`
        """
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))
        self.log.info('Initializing main window')

        # Initialize instance variable
        self.win_size = win_size

        # Initialize inherited class
        super().__init__()
        self.title(WindowSettings.title)
        self.geometry(f'+{self.center_coordinates[0]}+{self.center_coordinates[1]}') # Center the window to the screen
        self.minsize(self.win_size[0], self.win_size[1])

        # Set the main icons of the application
        if WindowSettings.win_icon is not None:
            self.iconbitmap(WindowSettings.win_icon)
        if WindowSettings.taskbar_icon is not None:
            from tkinter import PhotoImage
            self.iconphoto(True, PhotoImage(file=WindowSettings.taskbar_icon))

        # Change protocol when window is closed
        self.protocol('WM_DELETE_WINDOW', self.quit)

        # Add Ctrl+Q bind to close app
        self.bind('<Control-q>', self.quit)

        # Set the sidebar for the tabs
        self.sidebar = Sidebar(self)
        self.sidebar.pack(anchor='nw', fill='y', side='left', padx=4, pady=8)

        # Set the main container for the layouts
        self.main_frame = CTkFrame(self, fg_color=('#E7EBEF', '#293138'), corner_radius=4)
        self.main_frame.pack(anchor='nw', expand=True, fill='both', side='left', padx=6, pady=8)

        # Set the layouts and tabs
        self.layout_home = Home(self.main_frame, 'Gestion des casques') # Calling the widget to link it to the main_frame
        self.sidebar.add_tab(self.layout_home, tab_name='Gestion des casques', icon_name='home', default=True) # Using the add_tab function to load it into the sidebar, and voilà!

        self.layout_biblio = LogConsole(self.main_frame, 'Gestion de la bibliothèque') 
        self.sidebar.add_tab(self.layout_biblio, tab_name='Gestion de la bibliothèque', icon_name='biblio') 

        self.layout_setting = CTkFrame(self.main_frame, fg_color=('#CCD7E0', '#313B47'))
        self.sidebar.add_tab(self.layout_setting, tab_name='Settings', icon_name='settings')

    def quit(self):
        """
        Custom function when the app is closed.
        """
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
        """
        Return the resolution size `[x, y]` of the screen.
        """
        return [self.winfo_screenwidth(), self.winfo_screenheight()]