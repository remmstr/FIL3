# Internal modules
from core.config import LoggerSettings
from ui.utils import CTkLoggingHandler
from ui.widgets.panel import ButtonHeader, PanelTemplate
from ui.widgets.console import ConsoleStream
from core.resource import FontLibrary, IconLibrary
from devices.biblioManager import BiblioManager

# Requirements modules
from customtkinter import (
    CTkOptionMenu,
    CTkFrame,
    CTkLabel
)

# Built-in modules
import logging


class Biblio(PanelTemplate):
    def __init__(self, parent, title) -> None:
        # Initialize inherited class
        super().__init__(
            parent=parent,
            title=title,
            fg_color=('#CCD7E0', '#313B47')
        )

        self.biblioManager = BiblioManager()

        # Création du cadre principal pour contenir les solutions de la bibliothèque
        solutions_frame = CTkFrame(self)
        solutions_frame.pack(padx=10, pady=10, fill="both", expand=True)


        # Affichage des solutions dans la bibliothèque
        for solution in self.biblioManager.liste_solutions:
            CTkLabel(solutions_frame, text=f"{solution.nom} ({solution.version})", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 10)).pack(anchor='w', padx=10, pady=2)

