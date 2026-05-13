"""
Dieses Modul implementiert eine einfache grafische Benutzeroberfläche (GUI) mit Tkinter.
Die GUI enthält einen Start-Button, der die Hauptfunktion aus dem Modul 'verschieben' aufruft,
und zeigt die Terminal-Ausgabe in einem scrollbaren Textfeld an.
"""

import sys
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import verschieben

class TerminalRedirector:
    """
    Klasse zur Umleitung der Standardausgabe (stdout und stderr) in ein Tkinter-Text-Widget.
    Ermöglicht die Anzeige von Konsolen-Ausgaben in der GUI.
    """
    def __init__(self, text_widget):
        """
        Initialisiert den TerminalRedirector.

        Args:
            text_widget: Das Tkinter-Text-Widget, in das die Ausgabe geleitet wird.
        """
        self.text_widget = text_widget

    def write(self, message):
        """
        Schreibt eine Nachricht in das Text-Widget.

        Args:
            message (str): Die zu schreibende Nachricht.
        """
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')

    def flush(self):
        """
        Flush-Methode für die Kompatibilität mit sys.stdout/sys.stderr.
        """
        pass

def start_function():
    """
    Funktion, die beim Drücken des Start-Buttons aufgerufen wird.
    Ruft die Hauptfunktion aus dem Modul 'verschieben' auf.
    """
    verschieben.main()

def run_gui():
    """
    Erstellt und startet die GUI-Anwendung.
    """
    root = tk.Tk()
    root.title("Simple GUI mit Start-Knopf")
    root.geometry("800x600")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    start_button = tk.Button(frame, text="Start", command=start_function)
    start_button.pack(pady=(0, 10))

    terminal_output = ScrolledText(frame, height=20, width=90, state='disabled')
    terminal_output.pack()

    # Umleitung der Standardausgabe in das Text-Widget
    sys.stdout = TerminalRedirector(terminal_output)
    sys.stderr = TerminalRedirector(terminal_output)

    root.mainloop()

if __name__ == "__main__":
    run_gui()