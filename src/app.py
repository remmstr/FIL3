import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from threading import Thread
import subprocess
import time
import traceback
import sys
import os
import re
import shutil
from gestionCasques import GestionCasques
from PIL import Image, ImageTk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(" FIL3 ")
        self.root.configure(bg="white")
        self.casques = GestionCasques.getInstance()
        self.config = self.casques.config  # Accès à la configuration
        self.progress_bars = {}

        self.create_widgets()

        self.tracking_thread = Thread(target=self.track_devices)
        self.tracking_thread.start()

    def create_widgets(self):
        # Menu
        menu_frame = tk.Frame(self.root, bg="white")
        menu_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Charger et afficher l'image redimensionnée
        self.load_image("resources/images/image.png", menu_frame)

        # Cadre pour l'APK disponible
        apk_frame = tk.Frame(menu_frame, bg="white", bd=1, relief=tk.SOLID)
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

        # Cadre pour le bouton d'installation
        button_frame = tk.Frame(menu_frame, bg="white")
        button_frame.pack(side=tk.TOP, pady=10)

        self.install_button = tk.Button(button_frame, text="INSTALLER", font=("Helvetica", 10, "bold"), command=self.installer_apks_et_solutions, bg="white")
        self.install_button.pack()

        # Tableau des casques
        table_frame = tk.Frame(self.root, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Custom.Treeview", background="white", fieldbackground="white", borderwidth=0)

        columns = ("#", "Nom", "Modèle", "Version APK", "JSON", "Solutions")
        self.treeview = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")
        self.treeview.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            self.treeview.heading(col, text=col, anchor=tk.CENTER)
            self.treeview.heading(col, text=col, command=lambda c=col: self.sort_column(self.treeview, c, False))

        self.treeview.column("#", width=30, anchor=tk.CENTER)
        self.treeview.column("Nom", width=150, anchor=tk.CENTER)
        self.treeview.column("Modèle", width=100, anchor=tk.CENTER)
        self.treeview.column("Version APK", width=100, anchor=tk.CENTER)
        self.treeview.column("JSON", width=50, anchor=tk.CENTER)
        self.treeview.column("Solutions", width=150, anchor=tk.CENTER)

        # Bouton Banque de solutions
        banque_button_frame = tk.Frame(self.root, bg="white")
        banque_button_frame.pack(side=tk.TOP, pady=10)
        self.banque_solutions_button = tk.Button(banque_button_frame, text="Banque de solutions", command=self.download_banque_solutions, bg="white")
        self.banque_solutions_button.pack(pady=10)

        # Debug area
        debug_frame = tk.Frame(self.root, bg="white")
        debug_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        debug_label = tk.Label(debug_frame, text="Fenêtre de débogage", bg="white", font=("Helvetica", 10, "bold"))  # Texte en gras
        debug_label.pack(side=tk.TOP, anchor='w')

        # Ajouter une barre de défilement
        self.debug_text = tk.Text(debug_frame, height=10)
        debug_scrollbar = tk.Scrollbar(debug_frame, command=self.debug_text.yview)
        self.debug_text.configure(yscrollcommand=debug_scrollbar.set)
        self.debug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        debug_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Redirect stdout to the debug text
        sys.stdout = self

    def load_image(self, path, parent):
        try:
            image = Image.open(path)
            image = image.resize((250, 100), Image.LANCZOS)  # Redimensionnement de l'image
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(parent, image=photo, bg="white")
            label.image = photo  # keep a reference!
            label.pack(side=tk.LEFT, pady=0)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")

    def afficher_casques(self):
        try:
            self.treeview.delete(*self.treeview.get_children())
            self.progress_bars.clear()

            # Mettre à jour les informations APK pour chaque marque
            marques = ["Oculus", "Pico", "Vive"]
            for marque in marques:
                version = self.config.get_apk_version(marque)
                self.apk_labels[marque.lower()].config(text=f"{marque} : {version}")

            for i, casque in enumerate(self.casques.liste_casques, 1):
                json_status = "✓" if casque.JSON_path != "Fichier JSON inexistant" else "✗"
                # Placeholder for solutions; update this with actual solution listing logic when available
                solutions_status = "N/A"
                item_id = self.treeview.insert("", "end", values=(i, casque.numero, casque.modele, casque.version_apk, json_status, solutions_status))
                self.progress_bars[casque.numero] = self.create_progress_bar(item_id)
        except Exception as e:
            self.handle_exception("Erreur lors de l'affichage des casques", e)

    def create_progress_bar(self, item_id):
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(self.treeview, orient="horizontal", length=100, mode="determinate", variable=progress_var)
        self.treeview.set(item_id, "Solutions", "")
        self.treeview.update_idletasks()
        return progress_var

    def installer_apks_et_solutions(self):
        Thread(target=self._installer_apks_et_solutions).start()

    def _installer_apks_et_solutions(self):
        try:
            for casque in self.casques.liste_casques:
                self.update_progress(casque.numero, 0)
                self.highlight_row(casque.numero, "yellow")
                if not self.install_apk_with_progress(casque):
                    self.update_progress(casque.numero, 100)
                    self.update_status(casque.numero, "Echec APK")
                    self.highlight_row(casque.numero, "red")
                    continue
                self.update_progress(casque.numero, 50)
                self.add_solution_with_progress(casque)
                self.update_progress(casque.numero, 100)
                self.update_status(casque.numero, "Solution Téléversée")
                self.highlight_row(casque.numero, "green")
        except Exception as e:
            self.handle_exception("Erreur lors de l'installation des APKs et des solutions", e)

    def install_apk_with_progress(self, casque):
        try:
            command = [self.config.adb_exe_path, "-s", casque.numero, "install", casque.marque.APK_path]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                self.update_progress_from_output(casque.numero, line)
            process.stdout.close()
            return_code = process.wait()
            if return_code != 0:
                self.handle_exception(f"Erreur lors de l'installation de l'APK pour {casque.numero}", f"Code de retour : {return_code}")
                return False
            return True
        except Exception as e:
            self.handle_exception(f"Erreur lors de l'installation de l'APK pour {casque.numero}", e)
            return False

    def add_solution_with_progress(self, casque):
        try:
            command = [self.config.adb_exe_path, "-s", casque.numero, "push", self.config.upload_path, self.config.upload_casque_path]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                self.update_progress_from_output(casque.numero, line)
            process.stdout.close()
            process.wait()
        except Exception as e:
            self.handle_exception(f"Erreur lors de l'ajout de la solution pour {casque.numero}", e)

    def update_progress_from_output(self, casque_numero, output):
        match = re.search(r'(\d+)%', output)
        if match:
            progress = int(match.group(1))
            self.update_progress(casque_numero, progress)

    def update_progress(self, casque_numero, value):
        progress_var = self.progress_bars.get(casque_numero)
        if progress_var:
            progress_var.set(value)
            self.root.update_idletasks()

    def highlight_row(self, casque_numero, color):
        items = self.treeview.get_children()
        for item in items:
            values = self.treeview.item(item, "values")
            if values[1] == casque_numero:
                self.treeview.tag_configure(casque_numero, background=color)
                self.treeview.item(item, tags=(casque_numero,))

    def update_status(self, casque_numero, status):
        items = self.treeview.get_children()
        for item in items:
            values = self.treeview.item(item, "values")
            if values[1] == casque_numero:
                self.treeview.set(item, column="Solutions", value=status)

    def archiver_casque(self):
        try:
            self.casques.archivage()
            self.log_debug("Archivage du casque terminé.")
        except Exception as e:
            self.handle_exception("Erreur lors de l'archivage du casque", e)

    def configurer_wifi(self):
        try:
            self.casques.share_wifi_to_ALL_casque()
            self.log_debug("Configuration du wifi terminée.")
        except Exception as e:
            self.handle_exception("Erreur lors de la configuration du wifi", e)

    def quit(self):
        self.root.destroy()

    def track_devices(self):
        while True:
            try:
                self.casques.refresh_casques()
                self.afficher_casques()
            except Exception as e:
                self.handle_exception("Erreur lors de l'actualisation des casques", e)
            time.sleep(10)  # Ajout d'un délai pour éviter une boucle trop rapide

    def download_banque_solutions(self):
        try:
            destination = filedialog.askdirectory()
            if destination:
                shutil.copytree(self.config.Banque_de_solution_path, os.path.join(destination, "Banque_de_solutions"))
                self.log_debug("Téléchargement du dossier Banque de solutions terminé.")
        except Exception as e:
            self.handle_exception("Erreur lors du téléchargement de la banque de solutions", e)

    def handle_exception(self, message, exception):
        self.log_debug(f"{message}: {exception}")
        traceback.print_exc(file=sys.stdout)

    def log_debug(self, message):
        self.debug_text.insert(tk.END, message + "\n")
        self.debug_text.see(tk.END)

    def write(self, message):
        self.log_debug(message)

    def flush(self):
        pass  # Nécessaire pour rediriger stdout

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
