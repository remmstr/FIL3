import tkinter as tk  # Import nécessaire pour les variables tkinter

# Internal modules
from core.resource import FontLibrary, IconLibrary, ImageLibrary
from ui.widgets import PopupWindow
from devices import CasquesManager
from devices import Casque
from threading import Thread

# Requirements modules
from tktooltip import ToolTip
from customtkinter import (
    CTkButton,
    CTkFrame,
    CTkScrollableFrame,
    CTkLabel
)

# Built-in modules
import logging


class TableOfCasques(CTkFrame):
    """
    Module that creates the table of casques:
    - A header at the top that can hold an image OR a text
    - A menu with a vertical list of tabs
    - A footer that is configurable
    """

    def __init__(self, parent, title: str | None = None, image_name: str | None = None):
        """
        Create a new Table widget
        """
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

        # Initialize inherited class
        super().__init__(parent)

        # Initialize instance variables
        self.lines = []  # List to keep track of Line objects
        self.selected = None

        # Set the frame for the tab list of casques
        self.menu = CTkScrollableFrame(self)
        self.menu.configure(fg_color='transparent', corner_radius=0)
        self.menu._scrollbar.configure(width=32)  # Adjust scrollbar width
        self.menu.pack(expand=True, side='top', fill='both')

        self.casques = CasquesManager()
        self.add_lines()

    def refresh_table(self):
        """
        Refresh the table by updating existing lines or adding new ones if necessary.
        """

        # Obtenir la liste actuelle des casques
        current_casques = self.casques.get_liste_casque()

        # Rafraîchir les lignes existantes ou en ajouter de nouvelles
        existing_casque_numbers = [line.casque.numero for line in self.lines]

        # Rafraîchir les lignes existantes
        for line in self.lines:
            # Vérifier si le numéro du casque de la ligne existe toujours
            matching_casque = next((casque for casque in current_casques if casque.numero == line.casque.numero), None)
            if matching_casque:
                #print(f"Refreshing line for casque: {line.casque.numero}")  # Debug print
                line.refresh_line(matching_casque)  # Rafraîchir la ligne avec les nouvelles informations
            else:
                print(f"Casque {line.casque.numero} no longer exists, removing.")  # Debug print
                line.destroy()  # Supprimer la ligne si le casque n'existe plus
                self.lines.remove(line)

        # Ajouter de nouvelles lignes pour les casques restants qui ne sont pas encore affichés
        for casque in current_casques:
            if casque.numero not in existing_casque_numbers:
                print(f"Adding new line for casque: {casque.numero}")  # Debug print
                self.add_line(casque)



    def add_lines(self):
        """
        Add all lines to the table initially.
        """
        print("Adding initial lines...")  # Debug print
        if self.casques:
            for casque in self.casques.get_liste_casque():
                self.add_line(casque)

    def add_line(self, casque: Casque):
        """
        Add a new line to the table for each casque.
        """
        print(f"Creating line for casque: {casque.device}")  # Debug print
        line = Line(self.menu, casque)
        self.lines.append(line)
        line.pack(anchor='ne', side='top', expand=True, fill='x', padx=1, pady=1)


class Line(CTkFrame):
    """
    Custom button for the tabs in the sidebar.
    """

    def __init__(self, parent, casque: Casque):
        """
        Create a new tab for the sidebar.
        """
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

        # Initialize inherited class
        super().__init__(parent)

        self.casque = casque  # Keep reference to the casque object

        # Initialize StringVars for dynamic data
        self.casque_id_var = tk.StringVar(value=f"ID : {casque.numero}")
        self.casque_name_var = tk.StringVar(value=f"ID : {casque.name}")
        self.casque_model_var = tk.StringVar(value=f"{casque.modele}")
        self.casque_battery_var = tk.StringVar(value=f"Batt: {casque.battery_level}")
        is_connected, ssid = casque.is_wifi_connected()
        wifi_status = f"{ssid}" if is_connected else "Please Connect Wifi"
        self.casque_wifi_var = tk.StringVar(value=f"Wifi: {wifi_status}")
        self.casque_apk_var = tk.StringVar(value=f"APK : {casque.version_apk}")
        self.casque_code_var = tk.StringVar(value=f"Code association : {casque.code}")
        self.casque_exp_installed_var = tk.StringVar(value=f"[ {len(casque.getListSolInstall())} ] expériences installées")
        self.casque_exp_available_var = tk.StringVar(value=f"[ {len(casque.solutions_casque)} ] expériences disponibles")

        # UI Setup using StringVar
        self.create_widgets()

    def create_widgets(self):
        """
        Create widgets for the line using StringVar.
        """
        print(f"Creating widgets for casque: {self.casque.device}")  # Debug print

        self.info_casque1 = CTkFrame(self, fg_color='transparent')
        self.info_casque1.pack(anchor='w', side='left', padx=8)

        self.title_id = CTkLabel(self.info_casque1, textvariable=self.casque_id_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title_id.pack(anchor='w', expand=True, side='top', fill='x', padx=2)
        self.title_model = CTkLabel(self.info_casque1, textvariable=self.casque_model_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title_model.pack(anchor='w', expand=True, side='top', fill='x', padx=2)
        self.title_battery = CTkLabel(self.info_casque1, textvariable=self.casque_battery_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title_battery.pack(anchor='w', side='left', padx=4)
        self.title_wifi = CTkLabel(self.info_casque1, textvariable=self.casque_wifi_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title_wifi.pack(anchor='w', side='right', padx=4)

        self.info_casque3 = CTkFrame(self, fg_color='transparent')
        self.info_casque3.pack(anchor='w', side='left', padx=8)

        self.button_install = ButtonLine(self.info_casque3, tooltip='install app', icon_name='upload', command=lambda: self.install_apk(self.casque))
        self.button_install.pack(anchor='e', side='left')
        self.button_uninstall = ButtonLine(self.info_casque3, tooltip='uninstall app', icon_name='close', command=lambda: self.uninstall_apk(self.casque))
        self.button_uninstall.pack(anchor='e', side='left')
        self.title_apk = CTkLabel(self.info_casque3, textvariable=self.casque_apk_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title_apk.pack(anchor='w', expand=True, side='left', fill='y', padx=8)
        self.button_close = ButtonLine(self.info_casque3, tooltip='close app', icon_name='close', command=lambda: self.close_apk(self.casque))
        self.button_close.pack(anchor='w', side='right')
        self.button_open = ButtonLine(self.info_casque3, tooltip='open', icon_name='visible', command=lambda: self.start_apk(self.casque))
        self.button_open.pack(anchor='w', side='right')

        self.info_serveur_case = CTkFrame(self, fg_color='transparent', border_width=2)
        self.info_serveur_case.pack(anchor='w', side='top', padx=8, ipady=4, pady=6, ipadx=2)
        
        self.info_serveur = CTkFrame(self.info_serveur_case, height=1, width=1, fg_color='transparent')
        self.info_serveur.pack(anchor='w', side='left', padx=8)

        self.button_refresh = ButtonLine(self.info_serveur, text="Info serveur", tooltip='synchronosation_serveur', icon_name='refresh', command=lambda: self.refresh_json(self.casque))
        self.button_refresh.pack(anchor='w', side='top', pady=2)
        self.title_code = CTkLabel(self.info_serveur, textvariable=self.casque_name_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='ne')
        self.title_code.pack(anchor='ne', side='top', fill='both', padx=3)
        self.title_code = CTkLabel(self.info_serveur, textvariable=self.casque_code_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='ne')
        self.title_code.pack(anchor='ne', side='top', fill='both', padx=3)

        # Ensure info_serveur2 is properly created and packed
        self.info_serveur_droite = CTkFrame(self.info_serveur_case, fg_color='transparent')
        self.info_serveur_droite.pack(anchor='w', side='right', padx=8)  # Add pack() here to ensure it's displayed

        self.info_serveur2 = CTkFrame(self.info_serveur_droite, fg_color='transparent')
        self.info_serveur2.pack(anchor='se', expand=True, side='bottom', padx=8)  # Add pack() here to ensure it's displayed

        self.title_code = CTkLabel(self.info_serveur2, text="Tokens : Reverto", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 10), anchor='se')
        self.title_code.pack(anchor='se', side='right', fill='both', padx=12)
        self.title_code = CTkLabel(self.info_serveur2, text="Entreprise : Reverto", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 10), anchor='se')
        self.title_code.pack(anchor='se', side='right', fill='both', padx=12)



        self.info_serveur3 = CTkFrame(self.info_serveur_droite, fg_color='transparent')
        self.info_serveur3.pack(anchor='w', side='top', padx=8)  # Add pack() here to ensure it's displayed

        self.button_pull = ButtonLine(self.info_serveur3, tooltip='copier expéri. du casque dans la biblio', icon_name='pull', command=lambda: self.pull_solutions(self.casque))
        self.button_pull.pack(anchor='n', side='right')
        self.title_exp_installed = CTkLabel(self.info_serveur3, textvariable=self.casque_exp_installed_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title_exp_installed.pack(anchor='n', expand=True, side='right', fill='x', padx=4, pady=0)
        self.button_push = ButtonLine(self.info_serveur3, tooltip='push experi. disponible', icon_name='right', command=lambda: self.push_solutions(self.casque))
        self.button_push.pack(anchor='n', side='right')
        self.title_exp_available = CTkLabel(self.info_serveur3, textvariable=self.casque_exp_available_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title_exp_available.pack(anchor='n', expand=True, side='right', fill='x', padx=4, pady=0)
        self.button_settings = ButtonLine(self.info_serveur3, tooltip='Setting expériences(s)', icon_name='visible', command=lambda: self.setting_experiences_popup(self.casque) )
        self.button_settings.pack(anchor='n', side='right', padx=2)


    def refresh_line(self, casque: Casque):
        """
        Update the StringVars to reflect the latest information about the casque.
        """
        self.casque_id_var.set(f"ID : {casque.numero}")
        self.casque_name_var.set(f"Name : {casque.name}")
        self.casque_model_var.set(f"{casque.modele}")
        self.casque_battery_var.set(f"Batt: {casque.battery_level}")

        is_connected, ssid = casque.is_wifi_connected()
        wifi_status = f"{ssid}" if is_connected else "Please Connect Wifi"
        self.casque_wifi_var.set(f"Wifi: {wifi_status}")

        self.casque_apk_var.set(f"APK : {casque.version_apk}")
        self.casque_code_var.set(f"Code association : {casque.code}")
        self.casque_exp_installed_var.set(f"[ {len(casque.getListSolInstall())} ] expériences installées")
        self.casque_exp_available_var.set(f"[ {len(casque.solutions_casque)} ] expériences disponibles")

    def setting_experiences_popup(self, casque):
        """
        Opens a popup window to display and manage the solutions associated with a specific casque.
        
        Args:
            casque: The Casque object for which to open the solutions manager.
        """
            # Check if the popup already exists
        if hasattr(self, 'popup_experiences') and self.popup_experiences.winfo_exists():
            # If it exists, bring it to the front
            self.popup_experiences.lift()
            self.popup_experiences.focus_force()
            return
    
        # Create Popup Window
        self.popup_experiences = PopupWindow(win_title=f"Licence associée au casque {casque.name}", win_size=(600, 400))

        # Frame for Installed Solutions on Casque
        installed_frame = CTkFrame(self.popup_experiences)
        installed_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Label for Installed Solutions
        CTkLabel(installed_frame, text="Expériences installées sur le casque:", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 18)).pack(anchor='w', padx=5, pady=5)

        # Display Installed Solutions
        for solution in casque.solutions_casque:
            if solution.sol_install_on_casque:
                CTkLabel(installed_frame, text=f"{solution.nom} ({solution.version})", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 10)).pack(anchor='w', padx=10, pady=2)

        # Frame for Installed Solutions on Casque
        uninstalled_frame = CTkFrame(self.popup_experiences)
        uninstalled_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Label for Installed Solutions
        CTkLabel(uninstalled_frame, text="Expériences pas installées sur le casque:", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 18)).pack(anchor='w', padx=5, pady=5)

        # Frame for Solutions Available in Library
        library_frame = CTkFrame(uninstalled_frame)
        library_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Label for Solutions in Library
        CTkLabel(library_frame, text="Solutions disponibles dans la bibliothèque:", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11)).pack(anchor='w', padx=5, pady=5)

        # Display Solutions Available in Library
        for solution in casque.solutions_casque:
            if not solution.sol_install_on_casque and casque.is_solution_in_library(solution):
                CTkLabel(library_frame, text=f"{solution.nom} ({solution.version})", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 10)).pack(anchor='w', padx=10, pady=2)

        # Frame for Other Solutions
        other_frame = CTkFrame(uninstalled_frame)
        other_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Label for Other Solutions
        CTkLabel(other_frame, text="Autres solutions non disponibles:", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11)).pack(anchor='w', padx=5, pady=5)

        # Display Other Solutions
        for solution in casque.solutions_casque:
            if not solution.sol_install_on_casque and not casque.is_solution_in_library(solution):
                CTkLabel(other_frame, text=f"{solution.nom} ({solution.version})", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 10)).pack(anchor='w', padx=10, pady=2)

        # Close Button
        close_button = CTkButton(self.popup_experiences, text="Fermer", command=self.popup_experiences.close)
        close_button.pack(pady=10,side='bottom')


        
    def install_apk(self, casque):
        Thread(target=casque.install_APK).start()

    def uninstall_apk(self, casque):
        Thread(target=casque.uninstall_APK).start()

    def start_apk(self, casque):
        Thread(target=casque.open_apk).start()

    def close_apk(self, casque):
        Thread(target=casque.close_apk).start()

    def push_solutions(self, casque):
        Thread(target=casque.push_solutions).start()

    def pull_solutions(self, casque):
        Thread(target=casque.pull_solutions).start()

    def refresh_json(self, casque):
        Thread(target=casque.refresh_JSON).start()


class ButtonLine(CTkButton):
    """
    Template for a button that can be set in a panel header.
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
            width = kwargs.pop('width', 140)

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
