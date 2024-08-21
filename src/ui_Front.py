import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys
import http.client
from config import Config
from biblioManager import BiblioManager
from casquesManager import CasquesManager

class UI_Front:
    def __init__(self, root, app):
        """
        Initialise l'interface utilisateur (UI) principale pour l'application.

        Args:
            root: La fenêtre racine de Tkinter.
            app: L'application principale à laquelle cette interface est liée.
        """
        self.root = root
        self.app = app
        self.casques = CasquesManager()
        self.biblio = BiblioManager()
        self.progress_bars = {}
        self.widget_cache = {}
        self.config = Config()

    # ---------------------------------------------------------------------------
    # Initial Setup Functions
    # ---------------------------------------------------------------------------

    def create_widgets(self):
        """
        Crée les widgets principaux de l'interface utilisateur.
        """
        self.root.configure(bg="white")  # Assurer que le fond de l'application est blanc
        self.root.geometry("1500x800")  # Définir la taille de la fenêtre

        # Menu
        menu_frame = tk.Frame(self.root, bg="white")
        menu_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Charger et afficher l'image redimensionnée
        self.load_image(self.config.img_path_menu, menu_frame)

        # Bouton d'installation
        self.create_install_button(menu_frame)

        # Créer le menu déroulant pour APK
        self.create_apk_dropdown(menu_frame)

        # Table Frame
        self.create_table_frame()

        # Boutons pour la bibliothèque
        self.create_solution_buttons()

        # Zone de débogage
        self.create_debug_area()

        # Indicateur de statut de connexion
        self.connection_status_label = tk.Label(menu_frame, text="", bg="white", font=("Helvetica", 10, "bold"))
        self.connection_status_label.pack(side=tk.RIGHT, padx=10)
        self.update_connection_status()
        self.update_biblio_button_text()

        # Démarrer la mise à jour des barres de progression
        self.update_progress_bars()

        # Rediriger stdout vers la zone de débogage
        sys.stdout = self

    # ---------------------------------------------------------------------------
    # Helper Functions
    # ---------------------------------------------------------------------------

    def load_image(self, path, parent):
        """
        Charge et affiche une image dans le cadre parent spécifié.

        Args:
            path (str): Chemin vers l'image à charger.
            parent: Le cadre parent dans lequel l'image sera affichée.
        """
        try:
            image = Image.open(path)
            image = image.resize((250, 100), Image.LANCZOS)  # Redimensionnement de l'image
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(parent, image=photo, bg="white")
            label.image = photo  # Conserver une référence!
            label.pack(side=tk.LEFT, pady=0)
        except Exception as e:
            self.log_debug(f"Erreur lors du chargement de l'image : {e}")

    def create_install_button(self, parent):
        """
        Crée le bouton pour l'installation des APKs et des solutions.

        Args:
            parent: Le cadre parent dans lequel le bouton sera placé.
        """
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(side=tk.TOP, pady=10)

        self.install_button = tk.Button(button_frame, text="INSTALLER", font=("Helvetica", 10, "bold"), command=self.app.ui_back.installer_apks_et_solutions, bg="white")
        self.install_button.pack()

    def create_debug_area(self):
        """
        Crée la zone de débogage pour afficher les messages de log.
        """
        debug_frame = tk.Frame(self.root, bg="white")
        debug_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        debug_label = tk.Label(debug_frame, text="Fenêtre de débogage", bg="white", font=("Helvetica", 10, "bold"))
        debug_label.pack(side=tk.TOP, anchor='w')

        # Ajouter une barre de défilement
        self.debug_text = tk.Text(debug_frame, height=10)
        self.debug_scrollbar = tk.Scrollbar(debug_frame, command=self.debug_text.yview)
        self.debug_text.configure(yscrollcommand=self.debug_scrollbar.set, bg="white")
        self.debug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.debug_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_table_frame(self):
        """
        Crée le cadre de la table pour afficher les informations des casques.
        """
        self.table_frame = tk.Frame(self.root, bg="white")
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(self.table_frame, bg="white")
        self.scrollbar = tk.Scrollbar(self.table_frame, orient="vertical", command=canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Ajouter les en-têtes de colonnes
        self.create_table_headers()

    def create_table_headers(self):
        """
        Crée les en-têtes pour la table des casques.
        """
        header = tk.Frame(self.scrollable_frame, bg="white")
        header.pack(fill="x")

        tk.Label(header, text="Batt", width=4, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="ID", width=20, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Name", width=7, anchor="center", bg="white", fg="blue", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Modèle", width=10, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="APK", width=20, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Wi-Fi", width=15, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="JSON", width=7, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Code", width=5, anchor="center", bg="white",fg="blue", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Entreprise", width=21, anchor="center", bg="white",fg="blue", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Solution associé", width=18, anchor="center", bg="white",fg="blue", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Solution installé", width=19, anchor="center", bg="white",fg="blue", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Barre de téléch.", width=12, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="+ d'infos", width=10, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")

    def create_solution_buttons(self):
        """
        Crée les boutons pour télécharger et afficher les solutions de la bibliothèque.
        """
        buttons_frame = tk.Frame(self.root, bg="white")
        buttons_frame.pack(side=tk.TOP, pady=10)

        self.banque_solutions_button = tk.Button(buttons_frame, text="Télécharger Biblio", command=self.app.ui_back.download_banque_solutions, bg="white")
        self.banque_solutions_button.pack(side=tk.LEFT, padx=5)

        # Récupérer le nombre de solutions dans la bibliothèque
        num_solutions = len(self.biblio.liste_solutions)
        
        # Mettre à jour le texte du bouton pour afficher le nombre de solutions
        button_text = f"Afficher Bibliothèque ({num_solutions} solutions)"
        self.biblio_solutions_button = tk.Button(buttons_frame, text=button_text, command=self.show_biblio_solutions, bg="white")
        self.biblio_solutions_button.pack(side=tk.LEFT, padx=5)

    def update_biblio_button_text(self):
        """
        Met à jour le texte sur le bouton 'Afficher Bibliothèque' pour refléter le nombre de solutions dans la bibliothèque.
        """
        num_solutions = len(self.biblio.liste_solutions)
        button_text = f"Afficher Bibliothèque ({num_solutions} solution(s))"
        self.biblio_solutions_button.config(text=button_text)
        self.root.after(5000, self.update_biblio_button_text)  # Vérifier à nouveau toutes les 5 secondes

    def show_biblio_solutions(self):
        """
        Ouvre une nouvelle fenêtre affichant toutes les solutions dans la bibliothèque avec leurs poids.
        """
        biblio_window = tk.Toplevel(self.root)
        biblio_window.title("Solutions de la Bibliothèque")

        solutions_list = tk.Text(biblio_window, wrap="word", width=100, height=20)
        solutions_list.pack(padx=10, pady=10, fill="both", expand=True)

        for solution in self.app.biblio_manager.liste_solutions:
            solutions_list.insert(tk.END, f"{solution.nom} \n")

        solutions_list.config(state=tk.DISABLED)

        close_button = tk.Button(biblio_window, text="Fermer", command=biblio_window.destroy)
        close_button.pack(pady=10)

    def create_apk_dropdown(self, parent):
        """
        Crée le menu déroulant pour sélectionner les APKs.

        Args:
            parent: Le cadre parent dans lequel le menu déroulant sera placé.
        """
        dropdown_frame = tk.Frame(parent, bg="white")
        dropdown_frame.pack(side=tk.RIGHT, pady=10)

        folder_label = tk.Label(dropdown_frame, text="Choisissez un dossier:", bg="white")
        folder_label.pack(side=tk.LEFT, padx=5)

        self.selected_folder = tk.StringVar()
        self.folder_menu = ttk.Combobox(dropdown_frame, textvariable=self.selected_folder)
        self.folder_menu.pack(side=tk.LEFT, padx=5)
        self.folder_menu.bind("<<ComboboxSelected>>", self.update_apk_folder)

        self.populate_folders()

    def populate_folders(self):
        """
        Remplit le menu déroulant avec les dossiers dans le répertoire APK et sélectionne le premier par défaut.
        """
        apk_dir = "apk"  # Supposons que les dossiers APK sont dans un répertoire nommé "apk"
        folders = [d for d in os.listdir(apk_dir) if os.path.isdir(os.path.join(apk_dir, d))]
        self.folder_menu['values'] = folders

        if folders:
            self.folder_menu.current(0)
            self.update_apk_folder(None)  # Définir le dossier par défaut

    def update_apk_folder(self, event):
        """
        Met à jour le dossier APK dans CasquesManager lorsque l'utilisateur sélectionne un dossier dans le menu déroulant.

        Args:
            event: L'événement déclenché par la sélection du dossier dans le menu déroulant.
        """
        selected_folder = self.selected_folder.get()
        self.app.casques.set_apk_folder(selected_folder)

    def afficher_casques(self):
        """
        Affiche la liste des casques dans l'interface utilisateur.
        """
        try:
            # Obtenez la liste des casques actuels
            casques_list = self.app.casques.get_liste_casque()

            # Supprimez les messages précédents s'il en existe
            for widget in self.scrollable_frame.winfo_children():
                if isinstance(widget, tk.Label) and "Veuillez brancher un ou plusieurs casques" in widget.cget("text"):
                    widget.destroy()

            # Si aucun casque n'est connecté, affichez le message
            if not casques_list:
                message = "Veuillez brancher un ou plusieurs casques"
                tk.Label(self.scrollable_frame, text=message, bg="white", fg="orange", font=("Helvetica", 14, "bold")).pack(pady=20)
            
            casques_to_remove = set(self.widget_cache.keys())

            for i, casque in enumerate(casques_list, 1):
                if casque.numero not in self.widget_cache:
                    self.widget_cache[casque.numero] = self.create_casque_row(i, casque)
                else:
                    self.update_casque_row(i, casque)
                casques_to_remove.discard(casque.numero)

            # Supprimer les casques débranchés de l'affichage
            for casque_num in casques_to_remove:
                self.widget_cache[casque_num].pack_forget()
                del self.widget_cache[casque_num]

        except Exception as e:
            self.app.handle_exception("Erreur lors de l'affichage des casques", e)

    def create_casque_row(self, index, casque):
        """
        Crée une ligne dans la table pour afficher les informations d'un casque.

        Args:
            index (int): L'index du casque dans la liste.
            casque: L'objet Casque contenant les informations à afficher.

        Returns:
            item_frame: Le cadre contenant les widgets pour la ligne du casque.
        """
        item_frame = tk.Frame(self.scrollable_frame, bg="white")
        item_frame.pack(fill="x")

        battery_text = f"{casque.battery_level}%"
        tk.Label(item_frame, text=battery_text, width=4, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")

        tk.Label(item_frame, text=casque.numero, width=20, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")
        tk.Label(item_frame, text=casque.name, width=7, anchor="center", bg="white", fg="blue", font=("Helvetica", 10)).pack(side="left")
        tk.Label(item_frame, text=casque.modele, width=10, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")

        version_frame = tk.Frame(item_frame, bg="white")
        version_frame.pack(side="left", fill="x")
        install_button = tk.Button(version_frame, text="install", width=4, fg="black", command=lambda c=casque: self.app.ui_back.install_apk(c), bg="white")
        install_button.pack(side="left", padx=0)
        uninstall_button = tk.Button(version_frame, text="✗", width=1, fg="red", command=lambda c=casque: self.app.ui_back.uninstall_apk(c), bg="white")
        uninstall_button.pack(side="left", padx=0)

        # Vérifiez s'il y a une APK installée et définissez la couleur du texte
        apk_text = casque.version_apk
        apk_color = "orange" if apk_text == "X" else "black"
        tk.Label(version_frame, text=apk_text, width=4, anchor="center", bg="white", fg=apk_color, font=("Helvetica", 10)).pack(side="left", padx=(5, 5))

        open_button = tk.Button(version_frame, text="open", width=4, fg="black", command=lambda c=casque: self.app.ui_back.start_apk(c), bg="white")
        open_button.pack(side="left", padx=0)
        close_button = tk.Button(version_frame, text="✗", width=1, fg="red", command=lambda c=casque: self.app.ui_back.close_apk(c), bg="white")
        close_button.pack(side="left", padx=2)

        # Vérifier l'état du Wi-Fi
        is_connected, ssid = casque.is_wifi_connected()
        wifi_status = f"{ssid}" if is_connected else "Please Connect Wifi"
        wifi_color = "black" if is_connected else "orange"
        tk.Label(item_frame, text=wifi_status, width=16, anchor="center", bg="white", fg=wifi_color, font=("Helvetica", 10)).pack(side="left")
        
        json_status = "✓" if casque.JSON_path != "Fichier JSON inexistant" else "X"
        
        # Définir la couleur de l'indicateur JSON en fonction de l'état de l'APK
        json_color = "orange" if apk_color == "black" and json_status == "X" else "black"

        json_frame = tk.Frame(item_frame, bg="white")
        json_frame.pack(side="left", fill="x")
        tk.Label(json_frame, text=json_status, width=2, anchor="center", bg="white", fg=json_color, font=("Helvetica", 10)).pack(side="left")
        refresh_button = tk.Button(json_frame, text="⟳", width=2, fg="blue", command=lambda c=casque: self.app.ui_back.refresh_json(c), bg="white")
        refresh_button.pack(side="left", padx=7)

        tk.Label(item_frame, text=casque.code, width=4, anchor="center", bg="white", fg="blue", font=("Helvetica", 10)).pack(side="left")
        tk.Label(item_frame, text=casque.getEntreprise(), width=25, anchor="center", bg="white", fg="blue", font=("Helvetica", 10)).pack(side="left")

        solutions_casque_text = f"{len(casque.solutions_casque)} solution(s)"
        tk.Label(item_frame, text=solutions_casque_text, width=9, anchor="w", bg="white", fg="blue", font=("Helvetica", 10)).pack(side="left", padx=(5, 0))

        install_solutions_button = tk.Button(item_frame, text="--> Push", width=0, fg="black", command=lambda c=casque: self.app.ui_back.push_solutions(c), bg="white")
        install_solutions_button.pack(side="left", padx=0)

        solutions_install_text = f"{len(casque.getListSolInstall())} solution(s)"
        tk.Label(item_frame, text=solutions_install_text, width=9, anchor="w", bg="white", fg="blue", font=("Helvetica", 10)).pack(side="left", padx=(5, 0))
        
        pull_button = tk.Button(item_frame, text="Pull", width=3, fg="black", command=lambda c=casque: self.app.ui_back.pull_solutions(c), bg="white")
        pull_button.pack(side="left", padx=0)

        gestion_image = Image.open(self.config.img_path_icon_setting)
        gestion_image = gestion_image.resize((15, 15), Image.LANCZOS)
        gestion_photo = ImageTk.PhotoImage(gestion_image)
        gestion_button = tk.Button(item_frame, image=gestion_photo, width=20, height=20, command=lambda c=casque: self.app.ui_back.open_solution_manager(c), bg="white")
        gestion_button.image = gestion_photo
        gestion_button.pack(side="left", padx=5)

        # Ajouter la barre de progression
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(item_frame, orient="horizontal", length=82, mode="determinate", variable=progress_var)
        progress_bar.pack(side="left", padx=2)
        self.progress_bars[casque.numero] = progress_var
        self.progress_bars[casque.numero].set(casque.download_progress)

        # Ajouter les informations supplémentaires
        info_suppl = "PPV1 Installée" if casque.old_apk_installed else ""
        tk.Label(item_frame, text=info_suppl, width=15, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")

        return item_frame


    def update_casque_row(self, index, casque):
        """
        Met à jour les informations pour un casque dans la table.

        Args:
            index (int): L'index du casque dans la liste.
            casque: L'objet Casque contenant les informations mises à jour.
        """
        item_frame = self.widget_cache[casque.numero]
        widgets = item_frame.winfo_children()

        # Mettre à jour le numéro, le modèle, la version APK, le statut JSON, le nombre de solutions
        battery_text = f"{casque.battery_level}%"
        widgets[0].config(text=battery_text)

        widgets[1].config(text=casque.numero)
        widgets[2].config(text=casque.name)
        widgets[3].config(text=casque.modele)

        # Mettre à jour les enfants de version_frame
        version_frame = widgets[4]
        version_widgets = version_frame.winfo_children()

        # Définir la couleur en fonction de la présence de l'APK
        apk_text = casque.version_apk
        apk_color = "orange" if casque.get_installed_apk_version() == "X" else "black"
        version_widgets[2].config(text=apk_text, fg=apk_color)  # version_apk label

        # Mettre à jour le statut Wi-Fi
        is_connected, ssid = casque.is_wifi_connected()
        wifi_status = f"{ssid}" if is_connected else "Please connect to Wifi"
        wifi_color = "black" if is_connected else "orange"
        widgets[5].config(text=wifi_status, fg=wifi_color)  # Wi-Fi status

        json_status = "✓" if casque.JSON_path != "Fichier JSON inexistant" else "X"

        # Définir la couleur de l'indicateur JSON en fonction de l'état de l'APK
        json_color = "orange" if apk_color == "black" and json_status == "X" else "black"

        json_frame = widgets[6]
        json_widgets = json_frame.winfo_children()
        json_widgets[0].config(text=json_status, fg=json_color)  # JSON status

        widgets[7].config(text=casque.code)  # code
        widgets[8].config(text=casque.getEntreprise())  # entreprise

        solutions_casque_text = f"{len(casque.solutions_casque)} solution(s)"
        widgets[9].config(text=solutions_casque_text)  # solutions count

        solutions_install_text = f"{len(casque.getListSolInstall())} solution(s)"
        widgets[11].config(text=solutions_install_text)  # solutions install count

        # Mettre à jour la barre de progression
        self.progress_bars[casque.numero].set(casque.download_progress)

        # Mettre à jour les informations supplémentaires
        info_suppl = "App PPV1 Installée" if casque.old_apk_installed else ""
        widgets[13].config(text=info_suppl)  # info supplémentaire


    def update_progress_bars(self):
        """
        Met à jour périodiquement les barres de progression en fonction de l'attribut download_progress de chaque casque.
        """
        for casque in self.app.casques.get_liste_casque():
            if casque.numero in self.progress_bars:
                self.progress_bars[casque.numero].set(casque.download_progress)
        self.root.after(1000, self.update_progress_bars)  # Re-vérifier chaque seconde

    def create_progress_bar(self, item_frame):
        """
        Crée une barre de progression pour le cadre spécifié.

        Args:
            item_frame: Le cadre dans lequel la barre de progression sera créée.

        Returns:
            progress_var: Une variable de contrôle pour la barre de progression.
        """
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(item_frame, orient="horizontal", length=100, mode="determinate", variable=progress_var)
        progress_bar.pack(side="left", padx=5)
        return progress_var

    def log_debug(self, message):
        """
        Insère un message de débogage dans la zone de texte de débogage.

        Args:
            message (str): Le message à afficher.
        """
        if self.app.running:
            self.root.after(0, self._log_debug, message)
        else:
            print(message)

    def _log_debug(self, message):
        """
        Insère un message de débogage dans la zone de texte de débogage.

        Args:
            message (str): Le message à afficher.
        """
        self.debug_text.insert(tk.END, message + "\n")
        self.debug_text.see(tk.END)

    def write(self, message):
        """
        Écrit un message dans la zone de texte de débogage (utilisé pour rediriger stdout).

        Args:
            message (str): Le message à écrire.
        """
        self.log_debug(message)

    def flush(self):
        """
        Méthode flush requise pour rediriger stdout.
        """
        pass  # Nécessaire pour rediriger stdout

    def update_connection_status(self):
        """
        Met à jour l'indicateur de statut de connexion.
        """
        connected = self.check_connection()
        status_text = "Connection PPV2 ●" if connected else "Succès connexion plateforme Web ●"
        color = "green" if connected else "red"
        self.connection_status_label.config(text=status_text, fg=color)
        self.root.after(5000, self.update_connection_status)  # Vérifier à nouveau toutes les 5 secondes

    def check_connection(self):
        """
        Vérifie la connexion au site web.

        Returns:
            bool: True si la connexion est réussie, sinon False.
        """
        try:
            conn = http.client.HTTPSConnection("plateforme-beta.reverto.fr", timeout=5)
            conn.request("HEAD", "/")
            response = conn.getresponse()
            return response.status == 200
        except Exception as e:
            self.log_debug(f"Erreur de connexion: {e}")
            return False
