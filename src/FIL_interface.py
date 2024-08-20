import tkinter as tk
from ui_Front import UI_Front
from ui_Back import UI_Back
import traceback
import threading
import re
import sys
from casquesManager import CasquesManager
from biblioManager import BiblioManager

import sys

### permet d'enlever tout les prints
import builtins
# Définir une nouvelle fonction print qui ne fait rien
def silent_print(*args, **kwargs):
    pass
# Redéfinir print pour qu'elle soit silencieuse
#builtins.print = silent_print


class FIL_interface:
    def __init__(self, root):
        """
        Initialise l'interface FIL en configurant les gestionnaires de casques et de bibliothèque,
        ainsi que l'interface utilisateur.

        Args:
            root (tk.Tk): L'objet racine de la fenêtre Tkinter.
        """
        self.running = True
        self.biblio_manager = BiblioManager()  # Initialiser biblio_manager ici
        self.casques = CasquesManager()
        self.config = self.casques.config  # Accès à la configuration

        self.ui_front = UI_Front(root, self)
        self.ui_back = UI_Back(self)
        self.ui_front.create_widgets()
        
        self.stop_event = threading.Event()
        self.tracking_thread = threading.Thread(target=self.ui_back.track_devices, args=(self.stop_event,))
        self.tracking_thread.start()

    def start(self):
        """
        Démarre la boucle principale de l'interface Tkinter et initialise les actions à la fermeture.
        """
        try:
            self.ui_front.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.ui_front.root.mainloop()
        finally:
            self.stop_event.set()  # Indiquer aux threads de s'arrêter
            self.tracking_thread.join()  # Attendre la fin des threads

    def on_closing(self):
        """
        Gère l'événement de fermeture de la fenêtre principale, arrête l'exécution et détruit la fenêtre.
        """
        self.running = False
        self.ui_front.root.destroy()

    def log_debug(self, message):
        """
        Enregistre un message de débogage dans l'interface utilisateur ou sur la console si l'interface est fermée.

        Args:
            message (str): Le message de débogage à enregistrer.
        """
        if self.running:
            self.ui_front.log_debug(message)
        else:
            print(message)

    def handle_exception(self, message, exception):
        """
        Gère les exceptions en enregistrant un message d'erreur et en affichant la trace complète.

        Args:
            message (str): Le message associé à l'exception.
            exception (Exception): L'exception qui s'est produite.
        """
        self.log_debug(f"{message}: {exception}")
        traceback.print_exc(file=sys.stdout)

    def update_progress(self, casque_numero, value):
        """
        Met à jour la barre de progression associée à un casque spécifique.

        Args:
            casque_numero (str): Le numéro du casque pour lequel mettre à jour la progression.
            value (int): La nouvelle valeur de progression (en pourcentage).
        """
        if self.running:
            progress_var = self.ui_front.progress_bars.get(casque_numero)
            if progress_var:
                progress_var.set(value)
            self.ui_front.root.update_idletasks()

    def update_progress_from_output(self, casque_numero, output):
        """
        Extrait et met à jour la progression depuis une sortie textuelle.

        Args:
            casque_numero (str): Le numéro du casque pour lequel mettre à jour la progression.
            output (str): La sortie textuelle contenant le pourcentage de progression.
        """
        match = re.search(r'(\d+)%', output)
        if match:
            progress = int(match.group(1))
            self.update_progress(casque_numero, progress)

    def highlight_row(self, casque_numero, color):
        """
        Met en surbrillance une ligne dans l'interface utilisateur pour un casque spécifique.

        Args:
            casque_numero (str): Le numéro du casque à mettre en surbrillance.
            color (str): La couleur de surbrillance.
        """
        if self.running:
            for item in self.ui_front.scrollable_frame.winfo_children():
                values = self.ui_front.treeview.item(item, "values")
                if values[1] == casque_numero:
                    self.ui_front.treeview.tag_configure(casque_numero, background=color)
                    self.ui_front.treeview.item(item, tags=(casque_numero,))

    def update_status(self, casque_numero, status):
        """
        Met à jour le statut d'une solution pour un casque spécifique dans l'interface utilisateur.

        Args:
            casque_numero (str): Le numéro du casque dont le statut doit être mis à jour.
            status (str): Le nouveau statut à afficher.
        """
        if self.running:
            for item in self.ui_front.scrollable_frame.winfo_children():
                values = self.ui_front.treeview.item(item, "values")
                if values[1] == casque_numero:
                    self.ui_front.treeview.set(item, column="Solutions", value=status)

if __name__ == "__main__":
    root = tk.Tk()
    app = FIL_interface(root)
    app.start()
