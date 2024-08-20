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
        try:
            self.ui_front.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.ui_front.root.mainloop()
        finally:
            self.stop_event.set()  # Indiquer aux threads de s'arrêter
            self.tracking_thread.join()  # Attendre la fin des threads

    def on_closing(self):
        self.running = False
        self.ui_front.root.destroy()


    def log_debug(self, message):
        if self.running:
            self.ui_front.log_debug(message)
        else:
            print(message)

    def handle_exception(self, message, exception):
        self.log_debug(f"{message}: {exception}")
        traceback.print_exc(file=sys.stdout)

    def update_progress(self, casque_numero, value):
        if self.running:
            progress_var = self.ui_front.progress_bars.get(casque_numero)
            if progress_var:
                progress_var.set(value)
            self.ui_front.root.update_idletasks()

    def update_progress_from_output(self, casque_numero, output):
        match = re.search(r'(\d+)%', output)
        if match:
            progress = int(match.group(1))
            self.update_progress(casque_numero, progress)

    def highlight_row(self, casque_numero, color):
        if self.running:
            for item in self.ui_front.scrollable_frame.winfo_children():
                values = self.ui_front.treeview.item(item, "values")
                if values[1] == casque_numero:
                    self.ui_front.treeview.tag_configure(casque_numero, background=color)
                    self.ui_front.treeview.item(item, tags=(casque_numero,))

    def update_status(self, casque_numero, status):
        if self.running:
            for item in self.ui_front.scrollable_frame.winfo_children():
                values = self.ui_front.treeview.item(item, "values")
                if values[1] == casque_numero:
                    self.ui_front.treeview.set(item, column="Solutions", value=status)

if __name__ == "__main__":
    root = tk.Tk()
    app = FIL_interface(root)
    app.start()
