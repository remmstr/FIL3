# Internal modules
from core.config import LoggerSettings
from ui.utils import CTkLoggingHandler
from ui.widgets.panel import ButtonHeader, PanelTemplate
from ui.widgets.table import TableOfCasques
from ui.panels import LogConsole
from core.resource import FontLibrary, IconLibrary
from devices import CasquesManager  # Importer pour accéder à la gestion des casques

# Requirements modules
from customtkinter import (
    CTkOptionMenu,
    CTkFrame,
    CTkLabel
)

# Built-in modules
import logging
import os

class Home(PanelTemplate):
    def __init__(self, parent, title) -> None:
        # Initialize inherited class
        super().__init__(
            parent=parent,
            title=title,
            fg_color=('#CCD7E0', '#313B47')
        )
        
        # Label for APK version
        self.description_apk = CTkLabel(self.header.widgets_frame, text="Version de l'apk : ", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 12), anchor='w')
        self.description_apk.pack(anchor='n', expand=True, side='left', fill='x', padx=3)

        # Dropdown for APK selection
        self.selectbox_apk = CTkOptionMenu(self.header.widgets_frame, values=[], command=self.update_apk_folder)
        self.selectbox_apk.pack(anchor='e', side='left', padx=4)
        self.populate_folders()  # Remplir les dossiers APK

        self.main_frame = CTkFrame(self, fg_color=('#E7EBEF', '#293138'), corner_radius=4)
        self.main_frame.pack(anchor='nw', expand=True, fill='both', side='top', padx=6, pady=8)

        # Set the Table for the list of casques
        self.TableOfCasques = TableOfCasques(self.main_frame)
        self.TableOfCasques.pack(expand=True, side='top', fill='both', padx=4, pady=8)

        # Create a separate frame for the console at the bottom
        self.console_frame = CTkFrame(self.main_frame, fg_color=('#E7EBEF', '#293138'), corner_radius=4)
        self.console_frame.pack(anchor='sw', expand=False, side='bottom', fill='x', padx=4, pady=8)

        self.console = LogConsole(self.console_frame, 'Console') 
        self.console.pack(anchor='sw', expand=True, fill='both', padx=4, pady=8)

    def populate_folders(self):
        """
        Remplit le menu déroulant avec les dossiers dans le répertoire APK et sélectionne le premier par défaut.
        """
        apk_dir = "apk"  # Supposons que les dossiers APK sont dans un répertoire nommé "apk"
        if not os.path.exists(apk_dir):
            os.makedirs(apk_dir)  # Créer le répertoire si nécessaire

        folders = [d for d in os.listdir(apk_dir) if os.path.isdir(os.path.join(apk_dir, d))]
        self.selectbox_apk.configure(values=folders)

        if folders:
            self.selectbox_apk.set(folders[0])  # Définir le dossier par défaut
            self.update_apk_folder(folders[0])  # Définir le dossier par défaut

    def update_apk_folder(self, selected_folder):
        """
        Met à jour le dossier APK dans CasquesManager lorsque l'utilisateur sélectionne un dossier dans le menu déroulant.

        Args:
            selected_folder: Le dossier sélectionné dans le menu déroulant.
        """
        casques_manager = CasquesManager()
        casques_manager.set_apk_folder(selected_folder)
