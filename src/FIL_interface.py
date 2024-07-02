import tkinter as tk
from ui_Front import UI_Front
from ui_Back import UI_Back
from gestionCasques import GestionCasques
import traceback
import threading
import re
import sys

class FIL_interface:
    def __init__(self, root):
        self.casques = GestionCasques.getInstance()
        self.config = self.casques.config  # Accès à la configuration
        self.ui_front = UI_Front(root, self)
        self.ui_back = UI_Back(self)
        self.ui_front.create_widgets()

        self.tracking_thread = threading.Thread(target=self.ui_back.track_devices)
        self.tracking_thread.start()

    def start(self):
        self.ui_front.root.mainloop()

    def log_debug(self, message):
        self.ui_front.log_debug(message)

    def handle_exception(self, message, exception):
        self.log_debug(f"{message}: {exception}")
        traceback.print_exc(file=sys.stdout)

    def update_progress(self, casque_numero, value):
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
        for item in self.ui_front.scrollable_frame.winfo_children():
            values = self.ui_front.treeview.item(item, "values")
            if values[1] == casque_numero:
                self.ui_front.treeview.tag_configure(casque_numero, background=color)
                self.ui_front.treeview.item(item, tags=(casque_numero,))

    def update_status(self, casque_numero, status):
        for item in self.ui_front.scrollable_frame.winfo_children():
            values = self.ui_front.treeview.item(item, "values")
            if values[1] == casque_numero:
                self.ui_front.treeview.set(item, column="Solutions", value=status)

if __name__ == "__main__":
    root = tk.Tk()
    app = FIL_interface(root)
    app.start()