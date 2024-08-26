# Built-in modules
import logging

# Requirements modules
from tktooltip import ToolTip
from customtkinter import (
    CTkOptionMenu
)

# Internal modules
from core.logger import ApplicationLog, CTkLoggingHandler
from ui.widgets import PanelTemplate, TextStream, ButtonHeader, TabButton

#~~~~~ PANELS ~~~~~#

class LogConsole(PanelTemplate):
    def __init__(self, parent, title) -> None:
        # Initialize inherited class
        super().__init__(
            parent=parent,
            title=title,
            fg_color=('#CCD7E0', '#313B47')
            )

        self.console = TextStream(self)
        self.console.pack(anchor='nw', expand=True, fill='both', side='top', padx=8)

        # Set the handler for the logger with the custom CTkHandler
        self.log_handler = CTkLoggingHandler(self.console, ApplicationLog.log_level)
        self.log_handler.setFormatter(logging.Formatter('\x1b[36m[%(levelname)s]\x1b[0m \x1b[37m[%(name)s]\x1b[0m %(message)s'))
        self.log.root.addHandler(self.log_handler)

        self.selectbox = CTkOptionMenu(self.header.button_frame, values=['Log1', 'Log2', 'Log3'], command=self.select_interpreter)
        self.selectbox.pack(anchor='e', side='left', padx=4)

        self.button_flush = ButtonHeader(self.header.button_frame, icon_name='eraser',command=self.console.flush)
        self.button_flush.pack(anchor='e', side='left')
        ToolTip(self.button_flush, msg='Flush console')

        self.select_interpreter('Log1')

    def select_interpreter(self, choice):
        self.log.info('Changing stream for {}'.format(choice))

from customtkinter import CTkFrame, CTkLabel
from ui.widgets import PanelTemplate, CasqueWidget

class GestionDesCasques(PanelTemplate):
    
    def __init__(self, parent, title="Gestion des casques") -> None:
        # Initialize inherited class
        super().__init__(
            parent=parent,
            title=title,
            fg_color=('#CCD7E0', '#313B47')
        )

        # Cadre pour contenir le contenu spécifique
        self.content_frame = CTkFrame(self)
        self.content_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Exemple d'ajout d'un label pour indiquer une section
        self.label_example = CTkLabel(self.content_frame, text="Informations sur les casques", font=("Helvetica", 16))
        self.label_example.pack(pady=(10, 5))

        # Cadre pour la liste des casques
        self.casques_frame = CTkFrame(self.content_frame)
        self.casques_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Ajouter des casques (exemple)
        self.add_casque("Casque 1", "Modèle A", "100%")
        self.add_casque("Casque 2", "Modèle B", "80%")
        self.add_casque("Casque 3", "Modèle C", "60%")
        self.add_casque("Casque 1", "Modèle A", "100%")
        self.add_casque("Casque 2", "Modèle B", "80%")
        self.add_casque("Casque 3", "Modèle C", "60%")
        self.add_casque("Casque 1", "Modèle A", "100%")
        self.add_casque("Casque 2", "Modèle B", "80%")
        self.add_casque("Casque 3", "Modèle C", "60%")
        self.add_casque("Casque 1", "Modèle A", "100%")
        self.add_casque("Casque 2", "Modèle B", "80%")
        self.add_casque("Casque 3", "Modèle C", "60%")
        self.add_casque("Casque 1", "Modèle A", "100%")
        self.add_casque("Casque 2", "Modèle B", "80%")
        self.add_casque("Casque 3", "Modèle C", "60%")
        self.add_casque("Casque 1", "Modèle A", "100%")
        self.add_casque("Casque 2", "Modèle B", "80%")
        self.add_casque("Casque 3", "Modèle C", "60%")
        self.add_casque("Casque 1", "Modèle A", "100%")
        self.add_casque("Casque 2", "Modèle B", "80%")
        self.add_casque("Casque 3", "Modèle C", "60%")
        

    def add_casque(self, name, model, battery):
        """
        Ajoute un widget de casque dans la liste des casques.
        """
        casque_widget = CasqueWidget(self.casques_frame, name, model, battery)
        casque_widget.pack(fill="x", pady=5)
