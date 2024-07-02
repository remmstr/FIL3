import subprocess
import re
import time
import shutil
from threading import Thread
from tkinter import filedialog
import tkinter as tk
import os

class UI_Back:
    def __init__(self, app):
        self.app = app
        self.casques = self.app.casques

    def installer_apks_et_solutions(self):
        Thread(target=self._installer_apks_et_solutions).start()

    def _installer_apks_et_solutions(self):
        try:
            for casque in self.casques.liste_casques:
                self.app.update_progress(casque.numero, 0)
                self.app.highlight_row(casque.numero, "yellow")
                if not self.install_apk_with_progress(casque):
                    self.app.update_progress(casque.numero, 100)
                    self.app.update_status(casque.numero, "Echec APK")
                    self.app.highlight_row(casque.numero, "red")
                    continue
                self.app.update_progress(casque.numero, 50)
                self.add_solution_with_progress(casque)
                self.app.update_progress(casque.numero, 100)
                self.app.update_status(casque.numero, "Solution Téléversée")
                self.app.highlight_row(casque.numero, "green")
        except Exception as e:
            self.app.handle_exception("Erreur lors de l'installation des APKs et des solutions", e)

    def install_apk_with_progress(self, casque):
        try:
            command = [self.app.config.adb_exe_path, "-s", casque.numero, "install", casque.marque.APK_path]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                self.app.update_progress_from_output(casque.numero, line)
            process.stdout.close()
            return_code = process.wait()
            if return_code != 0:
                self.app.handle_exception(f"Erreur lors de l'installation de l'APK pour {casque.numero}", f"Code de retour : {return_code}")
                return False
            return True
        except Exception as e:
            self.app.handle_exception(f"Erreur lors de l'installation de l'APK pour {casque.numero}", e)
            return False

    def add_solution_with_progress(self, casque):
        try:
            command = [self.app.config.adb_exe_path, "-s", casque.numero, "push", self.app.config.upload_path, self.app.config.upload_casque_path]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                self.app.update_progress_from_output(casque.numero, line)
            process.stdout.close()
            process.wait()
        except Exception as e:
            self.app.handle_exception(f"Erreur lors de l'ajout de la solution pour {casque.numero}", e)

    def open_solution_manager(self, casque):
        solution_window = tk.Toplevel(self.app.ui_front.root)
        solution_window.title(f"Solutions du casque {casque.numero}")

        solution_list = tk.Text(solution_window, wrap="word", width=50, height=20)
        solution_list.pack(padx=10, pady=10, fill="both", expand=True)

        for solution in casque.solutions:
            solution_list.insert(tk.END, f"{solution.nom} (Version : {solution.version})\n")

        solution_list.config(state=tk.DISABLED)

        close_button = tk.Button(solution_window, text="Fermer", command=solution_window.destroy)
        close_button.pack(pady=10)

    def track_devices(self):
        while True:
            try:
                self.casques.refresh_casques()
                self.app.ui_front.afficher_casques()
            except Exception as e:
                self.app.handle_exception("Erreur lors de l'actualisation des casques", e)
            time.sleep(5)

    def download_banque_solutions(self):
        try:
            destination = filedialog.askdirectory()
            if destination:
                shutil.copytree(self.app.config.Banque_de_solution_path, os.path.join(destination, "Banque_de_solutions"))
                self.app.log_debug("Téléchargement du dossier Banque de solutions terminé.")
        except Exception as e:
            self.app.handle_exception("Erreur lors du téléchargement de la banque de solutions", e)
