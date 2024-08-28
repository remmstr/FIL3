# Internal modules
from ui.widgets import PopupWindow

# Requirements modules
from customtkinter import CTkLabel, CTkProgressBar


class LoadingPopup(PopupWindow):
    """
    Simple little window that show a loading bar.
    Just a boilerplate, nothing finished.
    """

    def __init__(self, text: str, *args, **kw):
        # Initialize inherited class
        super().__init__(text, (256, 128), *args, **kw)
        self.text = text

        self.header = CTkLabel(self, text=text)
        self.header.pack(pady=20)

        self.progress = CTkProgressBar(self, orient="horizontal", length=100, mode="indeterminate")
        self.progress.pack(pady=10)
        self.progress.start()