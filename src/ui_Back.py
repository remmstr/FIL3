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


class UI_Back:
    def __init__(self, app):
        self.app = app
        self.casques = self.app.casques
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
        solution_window = tk.Toplevel(self.app.ui_front.root)
        solution_window.title(f"Solutions du casque {casque.numero}")

        solution_list = tk.Text(solution_window, wrap="word", width=50, height=20)
        solution_list.pack(padx=10, pady=10, fill="both", expand=True)

        for solution in casque.solutions_casque:
            if(solution.sol_install_on_casque):
                solution_list.insert(tk.END, f"{solution.nom} ({solution.version})\n", "install_on_casque")
            elif(casque.is_solution_in_library(solution)):
                solution_list.insert(tk.END, f"{solution.nom} ({solution.version})\n", "in_library")
            else:
                solution_list.insert(tk.END, f"{solution.nom} ({solution.version})\n")
        
        # Configurer la couleur du texte pour les solutions installe sur le casque
        solution_list.tag_config("install_on_casque", foreground="green")
        # Configurer la couleur du texte pour les solutions dans la bibliothèque
        solution_list.tag_config("in_library", foreground="blue")
        
        solution_list.config(state=tk.DISABLED)

        close_button = tk.Button(solution_window, text="Fermer", command=solution_window.destroy)
        close_button.pack(pady=10)

    def track_devices(self, stop_event):
        while not stop_event.is_set():
            try:
                while(1) :
                    self.casques.refresh_casques()
                    if self.app.running:  # Vérifiez si l'application est toujours en cours d'exécution
                        self.app.ui_front.afficher_casques()
                    time.sleep(2.5)
            except Exception as e:
                self.app.handle_exception("Erreur lors de l'actualisation des casques", e)
            #stop_event.wait(10)  # Attendre 10 secondes ou jusqu'à ce que l'événement soit déclenché

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

        
