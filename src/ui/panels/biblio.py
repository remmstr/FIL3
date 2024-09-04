# Internal modules
from core.config import LoggerSettings
from ui.utils import CTkLoggingHandler
from ui.widgets.panel import ButtonHeader, PanelTemplate
from ui.widgets.console import ConsoleStream
from core.resource import FontLibrary, IconLibrary
from devices.biblioManager import BiblioManager

# Requirements modules
from customtkinter import (
    CTkOptionMenu,
    CTkFrame,
    CTkLabel
)
import tkinter as tk  # Needed for StringVar

# Built-in modules
import logging
import time
import threading


class Biblio(PanelTemplate):
    def __init__(self, parent, title) -> None:
        # Initialize inherited class
        super().__init__(
            parent=parent,
            title=title,
            fg_color=('#CCD7E0', '#313B47')
        )

        self.biblioManager = BiblioManager()
        self.solution_vars = []  # To store StringVar objects for each solution

        # Create the main frame to contain library solutions
        self.solutions_frame = CTkFrame(self)
        self.solutions_frame.pack(padx=10, pady=10, fill="both", expand=True)

        print("Initializing Biblio panel and displaying initial solutions...")  # Debug print

        # Display initial solutions in the library
        self.display_solutions()

        self.biblio = BiblioManager()
        refresh_thread = threading.Thread(target=self.threadind_refresh_biblio_and_UI, daemon=True).start()

    def threadind_refresh_biblio_and_UI(self):

        while(1):
            self.biblio.refresh_biblio()
            self.refresh_biblio_UI()
            time.sleep(2)

    def display_solutions(self):
        """
        Display all solutions in the library initially.
        """
        print("Displaying solutions...")  # Debug print

        # Clear the frame first
        for widget in self.solutions_frame.winfo_children():
            widget.destroy()

        # Display the solutions with StringVar
        self.solution_vars.clear()  # Clear the list of StringVars

        for solution in self.biblioManager.liste_solutions:
            solution_var = tk.StringVar(value=f"{solution.nom} ({solution.version})")
            self.solution_vars.append(solution_var)  # Keep reference to the StringVar
            CTkLabel(self.solutions_frame, textvariable=solution_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 10)).pack(anchor='w', padx=10, pady=2)

        print(f"Displayed {len(self.solution_vars)} solutions.")  # Debug print

    def refresh_biblio_UI(self):
        """
        Refresh the solutions in the library by updating the StringVar for each solution.
        """
        print("Refreshing library...")  # Debug print

        # Get updated solutions list
        updated_solutions = self.biblioManager.liste_solutions
        print(f"Updated solutions count: {len(updated_solutions)}")  # Debug print

        # Update each solution's StringVar
        for i, solution in enumerate(updated_solutions):
            if i < len(self.solution_vars):
                print(f"Updating existing solution: {solution.nom} ({solution.version})")  # Debug print
                self.solution_vars[i].set(f"{solution.nom} ({solution.version})")
            else:
                print(f"Adding new solution: {solution.nom} ({solution.version})")  # Debug print
                # If there are more solutions than StringVars, add them dynamically
                solution_var = tk.StringVar(value=f"{solution.nom} ({solution.version})")
                self.solution_vars.append(solution_var)
                CTkLabel(self.solutions_frame, textvariable=solution_var, font=FontLibrary.get_font_tkinter('Inter 18pt', 'Bold', 10)).pack(anchor='w', padx=10, pady=2)

        print("Library refreshed.")  # Debug print

    def periodic_refresh(self):
        """
        Periodically refresh the library solutions using the Tkinter `after` method.
        """
        print("Executing periodic refresh...")  # Debug print
        self.refresh_biblio()  # Refresh the solutions
        print("Scheduling next refresh...")  # Debug print
        self.after(10000, self.periodic_refresh)  # Schedule the next refresh after 10 seconds (10000 milliseconds)
