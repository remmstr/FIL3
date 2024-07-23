import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sys

class UI_Front:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.progress_bars = {}
        self.widget_cache = {}

    # ---------------------------------------------------------------------------
    # Initial Setup Functions
    # ---------------------------------------------------------------------------

    def create_widgets(self):
        """
        Create the main widgets for the UI.
        """
        self.root.configure(bg="white")  # Assurer que le fond de l'application est blanc
        self.root.geometry("1500x800")  # Augmenter la largeur de la fenêtre initiale

        # Menu
        menu_frame = tk.Frame(self.root, bg="white")
        menu_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Charger et afficher l'image redimensionnée
        self.load_image("resources/images/image.png", menu_frame)

        # APK Frame
        self.create_apk_frame(menu_frame)

        # Installation Button
        self.create_install_button(menu_frame)

        # Table Frame
        self.create_table_frame()

        # Banque de Solutions Button
        self.create_banque_button()

        # Ajouter le bouton pour afficher les solutions de la bibliothèque
        self.create_biblio_solutions_button()

        # Debug Area
        self.create_debug_area()

        # Start updating progress bars
        self.update_progress_bars()

        # Redirect stdout to the debug text
        sys.stdout = self

    # ---------------------------------------------------------------------------
    # Helper Functions
    # ---------------------------------------------------------------------------

    def load_image(self, path, parent):
        """
        Load and display an image in the specified parent frame.
        """
        try:
            image = Image.open(path)
            image = image.resize((250, 100), Image.LANCZOS)  # Redimensionnement de l'image
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(parent, image=photo, bg="white")
            label.image = photo  # keep a reference!
            label.pack(side=tk.LEFT, pady=0)
        except Exception as e:
            self.log_debug(f"Erreur lors du chargement de l'image : {e}")

    def create_apk_frame(self, parent):
        """
        Create the frame for displaying APK information.
        """
        apk_frame = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID)
        apk_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        apk_title = tk.Label(apk_frame, text="APK disponible", font=("Helvetica", 10, "bold"), bg="white")
        apk_title.pack(side=tk.TOP, pady=5)

        self.apk_labels = {
            "oculus": tk.Label(apk_frame, text="Oculus : ", font=("Helvetica", 9), bg="white"),
            "pico": tk.Label(apk_frame, text="Pico : ", font=("Helvetica", 9), bg="white"),
            "vive": tk.Label(apk_frame, text="Vive : ", font=("Helvetica", 9), bg="white"),
        }

        for label in self.apk_labels.values():
            label.pack(side=tk.TOP, anchor="w", padx=10, pady=2)

    def create_install_button(self, parent):
        """
        Create the button for installing APKs and solutions.
        """
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(side=tk.TOP, pady=10)

        self.install_button = tk.Button(button_frame, text="INSTALLER", font=("Helvetica", 10, "bold"), command=self.app.ui_back.installer_apks_et_solutions, bg="white")
        self.install_button.pack()

    def create_debug_area(self):
        """
        Create the debug area for displaying log messages.
        """
        debug_frame = tk.Frame(self.root, bg="white")
        debug_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        debug_label = tk.Label(debug_frame, text="Fenêtre de débogage", bg="white", font=("Helvetica", 10, "bold"))  # Texte en gras
        debug_label.pack(side=tk.TOP, anchor='w')

        # Ajouter une barre de défilement
        self.debug_text = tk.Text(debug_frame, height=10)
        self.debug_scrollbar = tk.Scrollbar(debug_frame, command=self.debug_text.yview)
        self.debug_text.configure(yscrollcommand=self.debug_scrollbar.set, bg="white")
        self.debug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.debug_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_table_frame(self):
        """
        Create the table frame for displaying casque information.
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

        # Add column headers
        self.create_table_headers()

    def create_table_headers(self):
        """
        Create headers for the casque table.
        """
        header = tk.Frame(self.scrollable_frame, bg="white")
        header.pack(fill="x")

        tk.Label(header, text="#", width=3, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Batt", width=3, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="ID", width=20, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Name", width=7, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Modèle", width=10, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="APK", width=10, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Wi-Fi", width=15, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="JSON", width=7, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Code", width=5, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Entreprise", width=20, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Solution associé", width=18, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Solution installé", width=18, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Barre de téléchar.", width=20, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Label(header, text="Info supplémentaire", width=20, anchor="center", bg="white", font=("Helvetica", 10, "bold")).pack(side="left")
        
    def create_banque_button(self):
        """
        Create the button for downloading solutions from the bank.
        """
        banque_button_frame = tk.Frame(self.root, bg="white")
        banque_button_frame.pack(side=tk.TOP, pady=10)
        self.banque_solutions_button = tk.Button(banque_button_frame, text="Banque de solutions", command=self.app.ui_back.download_banque_solutions, bg="white")
        self.banque_solutions_button.pack(pady=10)

    def create_biblio_solutions_button(self):
        """
        Create the button for displaying solutions from the library.
        """
        biblio_button_frame = tk.Frame(self.root, bg="white")
        biblio_button_frame.pack(side=tk.TOP, pady=10)
        self.biblio_solutions_button = tk.Button(biblio_button_frame, text="Afficher Solutions Bibliothèque", command=self.show_biblio_solutions, bg="white")
        self.biblio_solutions_button.pack(pady=10)

    def show_biblio_solutions(self):
        """
        Open a new window displaying all solutions in the library with their weights.
        """
        biblio_window = tk.Toplevel(self.root)
        biblio_window.title("Solutions de la Bibliothèque")

        solutions_list = tk.Text(biblio_window, wrap="word", width=100, height=20)
        solutions_list.pack(padx=10, pady=10, fill="both", expand=True)

        for solution in self.app.biblio_manager.liste_solutions:
            solutions_list.insert(tk.END, f"{solution.nom} - {solution.size / 1024:.2f} KB\n")

        solutions_list.config(state=tk.DISABLED)

        close_button = tk.Button(biblio_window, text="Fermer", command=biblio_window.destroy)
        close_button.pack(pady=10)

    def afficher_casques(self):
        """
        Display the list of casques.
        """
        try:
            casques_to_remove = set(self.widget_cache.keys())

            for i, casque in enumerate(self.app.casques.liste_casques, 1):
                if casque.numero not in self.widget_cache:
                    self.widget_cache[casque.numero] = self.create_casque_row(i, casque)
                else:
                    self.update_casque_row(i, casque)
                casques_to_remove.discard(casque.numero)

            for casque_num in casques_to_remove:
                self.widget_cache[casque_num].pack_forget()
                del self.widget_cache[casque_num]

            # Mettre à jour les informations APK pour chaque marque
            marques = ["Oculus", "Pico", "Vive"]
            for marque in marques:
                version = self.app.config.get_apk_version(marque)
                self.apk_labels[marque.lower()].config(text=f"{marque} : {version}")

        except Exception as e:
            self.app.handle_exception("Erreur lors de l'affichage des casques", e)

    def create_casque_row(self, index, casque):
        item_frame = tk.Frame(self.scrollable_frame, bg="white")
        item_frame.pack(fill="x")

        tk.Label(item_frame, text=index, width=3, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")
        tk.Label(item_frame, text=casque.battery_level, width=3, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")
        tk.Label(item_frame, text=casque.numero, width=20, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")
        tk.Label(item_frame, text=casque.name, width=7, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")
        tk.Label(item_frame, text=casque.modele, width=10, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")

        version_frame = tk.Frame(item_frame, bg="white")
        version_frame.pack(side="left", fill="x")
        install_button = tk.Button(version_frame, text="⇧", width=1, fg="green", command=lambda c=casque: self.app.ui_back.install_apk(c), bg="white")
        install_button.pack(side="left", padx=0)
        tk.Label(version_frame, text=casque.version_apk, width=4, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left", padx=(5, 5))
        uninstall_button = tk.Button(version_frame, text="✗", width=1, fg="red", command=lambda c=casque: self.app.ui_back.uninstall_apk(c), bg="white")
        uninstall_button.pack(side="left", padx=0)

        # Vérifier l'état du Wi-Fi
        is_connected, ssid = casque.is_wifi_connected()
        wifi_status = f"{ssid}" if is_connected else "Not Connected"
        tk.Label(item_frame, text=wifi_status, width=15, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")

        json_status = "✓" if casque.JSON_path != "Fichier JSON inexistant" else "X"
        tk.Label(item_frame, text=json_status, width=7, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")

        tk.Label(item_frame, text=casque.code, width=5, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")
        tk.Label(item_frame, text=casque.getEntreprise(), width=25, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")

        solutions_casque_text = f"{len(casque.solutions_casque)} solution(s)"
        tk.Label(item_frame, text=solutions_casque_text, width=9, anchor="w", bg="white", font=("Helvetica", 10)).pack(side="left", padx=(5, 0))

        install_solutions_button = tk.Button(item_frame, text="--> Push", width=0, fg="green", command=lambda c=casque: self.app.ui_back.push_solutions(c), bg="white")
        install_solutions_button.pack(side="left", padx=0)

        solutions_install_text = f"{len(casque.getListSolInstall())} solution(s)"
        tk.Label(item_frame, text=solutions_install_text, width=9, anchor="w", bg="white", font=("Helvetica", 10)).pack(side="left", padx=(5,0))

        gestion_image = Image.open("resources/images/parametres.png")
        gestion_image = gestion_image.resize((15, 15), Image.LANCZOS)
        gestion_photo = ImageTk.PhotoImage(gestion_image)
        gestion_button = tk.Button(item_frame, image=gestion_photo, width=10, height=10, command=lambda c=casque: self.app.ui_back.open_solution_manager(c), bg="white")
        gestion_button.image = gestion_photo
        gestion_button.pack(side="left", padx=5)

        # Ajouter la barre de progression
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(item_frame, orient="horizontal", length=150, mode="determinate", variable=progress_var)
        progress_bar.pack(side="left", padx=15)
        self.progress_bars[casque.numero] = progress_var

        # Ajouter les informations supplémentaires
        info_suppl = "PPV1 Installée" if casque.old_apk_installed else ""
        tk.Label(item_frame, text=info_suppl, width=20, anchor="center", bg="white", font=("Helvetica", 10)).pack(side="left")

        return item_frame

    def update_casque_row(self, index, casque):
        """
        Update the information for a casque in the table.
        """
        item_frame = self.widget_cache[casque.numero]
        widgets = item_frame.winfo_children()

        # Update index, numéro, modèle, version_apk, JSON status, solutions count
        widgets[0].config(text=index)
        widgets[1].config(text=casque.battery_level)
        widgets[2].config(text=casque.numero)
        widgets[3].config(text=casque.name)
        widgets[4].config(text=casque.modele)

        # Update version_frame children
        version_frame = widgets[5]
        version_widgets = version_frame.winfo_children()
        version_widgets[1].config(text=casque.version_apk)  # version_apk label

        # Update Wi-Fi status
        is_connected, ssid = casque.is_wifi_connected()
        wifi_status = f"{ssid}" if is_connected else "Not Connected"
        widgets[6].config(text=wifi_status)  # Wi-Fi status

        json_status = "✓" if casque.JSON_path != "Fichier JSON inexistant" else "X"
        widgets[7].config(text=json_status)  # JSON status

        widgets[8].config(text=casque.code)  # code
        widgets[9].config(text=casque.getEntreprise())  # entreprise

        solutions_casque_text = f"{len(casque.solutions_casque)} solution(s)"
        widgets[10].config(text=solutions_casque_text)  # solutions count

        solutions_install_text = f"{len(casque.getListSolInstall())} solution(s)"
        widgets[12].config(text=solutions_install_text)  # solutions install count

        # Mettre à jour la barre de progression
        self.progress_bars[casque.numero].set(casque.download_progress)

        # Mettre à jour les informations supplémentaires
        info_suppl = "App PPV1 Installée" if casque.old_apk_installed else ""
        widgets[13].config(text=info_suppl)  # info supplémentaire

    def update_progress_bars(self):
        """
        Periodically update the progress bars based on the download_progress attribute of each casque.
        """
        for casque in self.app.casques.liste_casques:
            if casque.numero in self.progress_bars:
                self.progress_bars[casque.numero].set(casque.download_progress)
        self.root.after(1000, self.update_progress_bars)  # Re-check every second

    def create_progress_bar(self, item_frame):
        """
        Create a progress bar for the specified item frame.
        """
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(item_frame, orient="horizontal", length=100, mode="determinate", variable=progress_var)
        progress_bar.pack(side="left", padx=5)
        return progress_var

    def log_debug(self, message):
        if self.app.running:
            self.root.after(0, self._log_debug, message)
        else:
            print(message)

    def _log_debug(self, message):
        """
        Insert a debug message into the debug text area.
        """
        self.debug_text.insert(tk.END, message + "\n")
        self.debug_text.see(tk.END)

    def write(self, message):
        """
        Write a message to the debug text area (used for redirecting stdout).
        """
        self.log_debug(message)

    def flush(self):
        """
        Flush method required for redirecting stdout.
        """
        pass  # Nécessaire pour rediriger stdout
