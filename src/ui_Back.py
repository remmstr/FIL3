import subprocess
import re
import time
import shutil
from threading import Thread
from tkinter import filedialog
import tkinter as tk
import os
from config import Config
import adbtools
from biblioManager import BiblioManager
from casquesManager import CasquesManager


class UI_Back:
    def __init__(self, app):
        self.app = app
        self.casques = CasquesManager()
        self.biblio = BiblioManager()
        self.config = Config()

    def installer_apks_et_solutions(self):
        try:
            for casque in self.casques.liste_casques:
                        Thread(target=self.installer_apks_et_solution(casque)).start()
        except Exception as e:
            self.app.handle_exception("Erreur lors de l'installation des APKs et des solutions", e)



    def installer_apks_et_solution(self,casque):
        try:
            self.install_apk(casque)
            while(casque.JSON_path == 'X') : pass
            time.sleep(1)
            self.push_solutions(casque)
        except Exception as e:
            self.app.handle_exception("Erreur lors del'installation des APKs et des solutions", e)

    def open_solution_manager(self, casque):
        # Renommer la fenêtre
        solution_window = tk.Toplevel(self.app.ui_front.root)
        solution_window.title(f"Licence associée au casque {casque.numero}")

        # Zone de texte pour afficher les solutions
        solution_list = tk.Text(solution_window, wrap="word", width=100, height=20)
        solution_list.pack(padx=10, pady=10, fill="both", expand=True)

        for solution in casque.solutions_casque:
            in_library = casque.is_solution_in_library(solution)  # Stocker le résultat
            print(f"Résultat de is_solution_in_library: {in_library}")

            if solution.sol_install_on_casque:
                solution_list.insert(tk.END, f"{solution.nom} ({solution.version})\n", "install_on_casque")
            elif in_library:
                solution_list.insert(tk.END, f"{solution.nom} ({solution.version})\n", "in_library")
                print(f"in library")
            else:
                print(f"casque.is_solution_in_library(solution): {in_library}")
                solution_list.insert(tk.END, f"{solution.nom} ({solution.version})\n")
                print(f"not in library")
                
        # Configurer la couleur du texte pour les solutions installées sur le casque
        solution_list.tag_config("install_on_casque", foreground="green")
        # Configurer la couleur du texte pour les solutions dans la bibliothèque
        solution_list.tag_config("in_library", foreground="blue")
        
        solution_list.config(state=tk.DISABLED)

        # Ajouter la légende en bas de la fenêtre
        legend_frame = tk.Frame(solution_window, bg="white")
        legend_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(legend_frame, text="Légende : ", bg="white", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="Solution téléchargée dans le casque", fg="green", bg="white", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=10)
        tk.Label(legend_frame, text="Pas téléchargée, disponible dans la bibliothèque", fg="blue", bg="white", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=20)
        tk.Label(legend_frame, text="Pas téléchargée", bg="white", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=10)

        # Bouton Fermer
        close_button = tk.Button(solution_window, text="Fermer", command=solution_window.destroy)
        close_button.pack(pady=10)


    def track_devices(self, stop_event):
        while not stop_event.is_set():
            try:
                while(1) :
                    self.casques.refresh_casques()
                    self.biblio.refresh_biblio()
                    if self.app.running:  # Vérifiez si l'application est toujours en cours d'exécution
                        self.app.ui_front.afficher_casques()
                    time.sleep(2.5)
            except Exception as e:
                self.app.handle_exception("Erreur lors de l'actualisation des casques", e)

    def download_banque_solutions(self):
        try:
            destination = filedialog.askdirectory()
            if destination:
                shutil.copytree(self.app.config.Banque_de_solution_path, os.path.join(destination, "Banque_de_solutions"))
                self.app.log_debug("Téléchargement du dossier Banque de solutions terminé.")
        except Exception as e:
            self.app.handle_exception("Erreur lors du téléchargement de la banque de solutions", e)

    def install_apk(self, casque):
        Thread(target=casque.install_APK).start()

    def uninstall_apk(self, casque):
        Thread(target=casque.uninstall_APK).start()

    def start_apk(self, casque):
        Thread(target=adbtools.start_application(self.config.adb_exe_path, casque.numero, self.config.package_name)).start()
        
    def close_apk(self, casque):
        Thread(target=adbtools.stop_application(self.config.adb_exe_path, casque.numero, self.config.package_name)).start()
        
    def push_solutions(self, casque):
        Thread(target=casque.push_solutions).start()

    def pull_solutions(self, casque):
        Thread(target=casque.pull_solutions).start()

    def refresh_json(self,casque):
        Thread(target=casque.refresh_casque_serveur).start()

        
