# Internal modules
from core.resource import FontLibrary, IconLibrary, ImageLibrary
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

        # Initialize instance variable
        self.tabs = {}
        self.selected = None

        # Set the frame for the tab list of casques
        self.menu = CTkScrollableFrame(self)
        self.menu.configure(fg_color='transparent', corner_radius=0)
        self.menu._scrollbar.configure(width=32)  # Adjust scrollbar width
        self.menu.pack(expand=True, side='top', fill='both')

        # Add each casque to the table
        casques = CasquesManager()
        if casques:
            for casque in casques.get_liste_casque():
                self.add_linee(casque)

    def set_header(self, title: str | None = None, image_name: str | None = None):
        """
        Set an image OR a title in the header (can't be both; the icon will be prioritized)
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

    def add_linee(self, casque: Casque):
        """
        Add a new tab to the sidebar for each casque
        """
        self.tabs.update({casque.device: Line(self.menu, casque)})
        self.tabs[casque.device].pack(anchor='ne', side='top', expand=True, fill='x', padx=1, pady=1)

    
    '''
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
        self.tabs[tab_name].pack(anchor='ne', side='top', expand=True, fill='x', padx=1, pady=1)
    '''



class Line(CTkFrame):
    """
    Custom button for the tabs in the sidebar
    """

    def __init__(self, parent, casque: Casque):
        """
        Create a new tab for the sidebar
        """
        # Set instance logger
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

        # Initialize inherited class
        super().__init__(parent)

        self.casque = casque
        
        #self.image_casque = CTkFrame(self, fg_color='transparent')
        #self.image_casque.pack(anchor='w', side='left', padx=8)
        #self.title = CTkLabel(self.image_casque, image='noname' )
        #self.title.pack(anchor='w', expand=True, side='top', fill='x', padx=2)

        self.info_casque1 = CTkFrame(self, fg_color='transparent')
        self.info_casque1.pack(anchor='w', side='left', padx=8)
        self.title = CTkLabel(self.info_casque1, text=f"ID : {casque.numero}", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title.pack(anchor='w', expand=True, side='top', fill='x', padx=2)
        self.title = CTkLabel(self.info_casque1, text=f"{casque.modele}", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title.pack(anchor='w', expand=True, side='top', fill='x', padx=2)

        # Vérifier l'état du Wi-Fi
        is_connected, ssid = casque.is_wifi_connected()
        wifi_status = f"{ssid}" if is_connected else "Please Connect Wifi"
        wifi_color = "black" if is_connected else "orange"

        self.title = CTkLabel(self.info_casque1, text=f"Batt: {casque.battery_level}   ", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title.pack(anchor='w', side='left', padx=4)
        self.title = CTkLabel(self.info_casque1, text=f"Wifi: {wifi_status}", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title.pack(anchor='w', side='right', padx=4)

        self.info_casque3 = CTkFrame(self, fg_color='transparent')
        self.info_casque3.pack(anchor='w', side='left', padx=8)
        self.button_clear = ButtonLine(self.info_casque3, tooltip='install app', icon_name='upload', command=lambda: self.install_apk(casque))
        self.button_clear.pack(anchor='e', side='left')
        self.button_clear = ButtonLine(self.info_casque3, tooltip='uninstall app', icon_name='close', command=lambda: self.uninstall_apk(casque))
        self.button_clear.pack(anchor='e', side='left')
        self.title = CTkLabel(self.info_casque3, text=f"APK : {casque.version_apk}", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title.pack(anchor='w', expand=True, side='left', fill='y', padx=8)
        self.button_clear = ButtonLine(self.info_casque3, tooltip='close app', icon_name='close', command=lambda: self.close_apk(casque))
        self.button_clear.pack(anchor='w', side='right')
        self.button_clear = ButtonLine(self.info_casque3, tooltip='open', icon_name='visible', command=lambda: self.start_apk(casque))
        self.button_clear.pack(anchor='w', side='right')
        

        self.info_serveur_case = CTkFrame(self, fg_color='transparent',border_width=2)
        self.info_serveur_case.pack(anchor='w', side='top', padx=8, ipady=4, pady=6, ipadx=2)
        self.info_serveur = CTkFrame(self.info_serveur_case, height=1,width=1, fg_color='transparent')
        self.info_serveur.pack(anchor='w', side='left', padx=8)

        self.button_clear = ButtonLine(self.info_serveur, text="Info serveur", tooltip='synchronosation_serveur', icon_name='refresh', command=lambda: self.refresh_json(casque))
        self.button_clear.pack(anchor='w', side='top', pady=2)
        
        self.title = CTkLabel(self.info_serveur, text="Entreprise associés : Reverto", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title.pack(anchor='w', side='bottom', fill='both', padx=2, ipady=0, pady=0)
        self.title = CTkLabel(self.info_serveur, text="Tokens associés : Reverto", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title.pack(anchor='n', side='bottom', fill='both', padx=2, ipady=0, pady=0)

        self.info_serveur2 = CTkFrame(self.info_serveur_case, fg_color='transparent')
        self.info_serveur2.pack(anchor='w', side='right', padx=8)
        self.title = CTkLabel(self.info_serveur2, text=f"Code association : {casque.code}", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 10), anchor='ne')
        self.title.pack(anchor='ne', side='top', fill='both', padx=3, )
        self.button_clear = ButtonLine(self.info_serveur2, tooltip='copier expéri. du casque dans la biblio', icon_name='pull', command=lambda: self.pull_solutions(casque))
        self.button_clear.pack(anchor='n', side='right')
        self.title = CTkLabel(self.info_serveur2, text=f"[ {len(casque.getListSolInstall())} ] expériences installées", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title.pack(anchor='n', expand=True, side='right', fill='x', padx=4, pady=0)
        self.button_clear = ButtonLine(self.info_serveur2, tooltip='push experi. disponible', icon_name='right', command=lambda: self.push_solutions(casque))
        self.button_clear.pack(anchor='n', side='right')
        self.title = CTkLabel(self.info_serveur2, text=f"[ {len(casque.solutions_casque)} ] expériennces disponible", font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 11), anchor='w')
        self.title.pack(anchor='n', expand=True, side='right', fill='x', padx=4, pady=0)
        self.button_clear = ButtonLine(self.info_serveur2, tooltip='Setting expériences(s)', icon_name='visible')
        self.button_clear.pack(anchor='n', side='right',padx=2)


        # Initialize instance variable
        self.casque.device = casque.device

    def install_apk(self, casque):
        """
        Installe l'APK sur un casque spécifique dans un thread séparé.

        Args:
            casque: L'objet Casque sur lequel installer l'APK.
        """
        Thread(target=casque.install_APK).start()

    def uninstall_apk(self, casque):
        """
        Désinstalle l'APK d'un casque spécifique dans un thread séparé.

        Args:
            casque: L'objet Casque sur lequel désinstaller l'APK.
        """
        Thread(target=casque.uninstall_APK).start()

    def start_apk(self, casque):
        """
        Démarre l'APK sur un casque spécifique dans un thread séparé.

        Args:
            casque: L'objet Casque sur lequel démarrer l'APK.
        """
        Thread(target=casque.open_apk()).start()

    def close_apk(self, casque):
        """
        Ferme l'APK sur un casque spécifique dans un thread séparé.

        Args:
            casque: L'objet Casque sur lequel fermer l'APK.
        """
        Thread(target=casque.close_apk()).start()

    def push_solutions(self, casque):
        """
        Téléverse les solutions sur un casque spécifique dans un thread séparé.

        Args:
            casque: L'objet Casque sur lequel téléverser les solutions.
        """
        Thread(target=casque.push_solutions).start()

    def pull_solutions(self, casque):
        """
        Récupère les solutions depuis un casque spécifique dans un thread séparé.

        Args:
            casque: L'objet Casque depuis lequel récupérer les solutions.
        """
        Thread(target=casque.pull_solutions).start()

    def refresh_json(self, casque):
        """
        Rafraîchit le fichier JSON sur un casque spécifique dans un thread séparé.

        Args:
            casque: L'objet Casque pour lequel rafraîchir le fichier JSON.
        """
        Thread(target=casque.refresh_JSON).start()




class ButtonLine(CTkButton):
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

