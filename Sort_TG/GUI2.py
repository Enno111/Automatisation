import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
import threading
import logging
from verschieben import aufträge_Verschieben

# Profile mit vordefinierten Verzeichnissen
profile_dict = {
    "TechnogymEssen1": {
        "dateipfad": r"X:\Scan aus ESS\Essen",
        "zielverzeichnis": r"X:\Mannheim\Technogym Digital",
        "archivverzeichnis": r"X:\Archiv SPA\Essen",
        "weiteres_zielverzeichnis": r"X:\Mannheim\Technogym Digital\1.Erledigt"
    },
    "TechnogymEssen2": {
        "dateipfad": r"X:\Scan aus MAN\Essen",
        "zielverzeichnis": r"X:\Mannheim\Technogym Digital",
        "archivverzeichnis": r"X:\Archiv SPA\Essen",
        "weiteres_zielverzeichnis": r"X:\Mannheim\Technogym Digital\1.Erledigt"
    },
    "TechnogymManheim1": {
        "dateipfad": r"X:\Scan aus MAN\Mannheim",
        "zielverzeichnis": r"X:\Mannheim\Technogym Digital",
        "archivverzeichnis": r"X:\Archiv SPA\Mannheim",
        "weiteres_zielverzeichnis": r"X:\Mannheim\Technogym Digital\1.Erledigt"
    },
    "TechnogymManheim2": {
        "dateipfad": r"X:\Scan aus ESS\Mannheim",
        "zielverzeichnis": r"X:\Mannheim\Technogym Digital",
        "archivverzeichnis": r"X:\Archiv SPA\Mannheim",
        "weiteres_zielverzeichnis": r"X:\Mannheim\Technogym Digital\1.Erledigt"
    }
}

class RedirectText:
    """ Klasse zur Umleitung der Standardausgabe in das GUI-Textfeld """
    def __init__(self, text_widget):
        self.output = text_widget

    def write(self, string):
        self.output.insert(tk.END, string)
        self.output.see(tk.END)

    def flush(self):
        pass


class TextHandler(logging.Handler):
    """Logging handler that writes logs to a Tk Text widget."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        try:
            msg = self.format(record) + "\n"
            # write in GUI thread
            def append():
                self.text_widget.configure(state='normal')
                self.text_widget.insert(tk.END, msg)
                self.text_widget.see(tk.END)
                self.text_widget.configure(state='disabled')
            self.text_widget.after(0, append)
        except Exception:
            pass

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Datei verschieben")
        self.root.geometry("650x500")
        
        # ttkbootstrap-Style setzen (modernes Design)
        style = ttk.Style(theme="darkly")  # Alternativen: 'flatly', 'superhero', 'solar', 'morph'
        self.root = style.master

        # Rahmen für UI
        frame = ttk.Frame(root, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        # Dropdown für Profilwahl
        ttk.Label(frame, text="Profil auswählen:").grid(row=0, column=0, sticky="w", pady=5)
        self.profil_combobox = ttk.Combobox(frame, values=list(profile_dict.keys()), state="readonly", bootstyle="primary")
        self.profil_combobox.grid(row=0, column=1, pady=5, sticky="ew")
        self.profil_combobox.bind("<<ComboboxSelected>>", self.profil_auswaehlen)

        # Felder speichern
        self.entries = {}

        # Eingabefelder mit Buttons
        felder = [
            ("ScanOrdner:", "dateipfad"),
            ("AuftragsOrdner:", "zielverzeichnis"),
            ("Archivverzeichnis:", "archivverzeichnis"),
            ("ErledigtOrdner:", "weiteres_zielverzeichnis")
        ]

        for i, (label, key) in enumerate(felder):
            ttk.Label(frame, text=label).grid(row=i+1, column=0, sticky="w", pady=5)
            entry = ttk.Entry(frame, width=50, bootstyle="info")
            entry.grid(row=i+1, column=1, pady=5, sticky="ew")
            button = ttk.Button(frame, text="Wählen", bootstyle="success-outline", command=lambda e=entry: self.pfad_waehlen(e))
            button.grid(row=i+1, column=2, padx=5, pady=5)
            self.entries[key] = entry  # Speichere die Entry-Widgets in einem Dictionary

        # Button zum Starten der Funktion
        self.run_button = ttk.Button(frame, text="Ausführen", bootstyle="danger", command=self.ausfuehren)
        self.run_button.grid(row=5, columnspan=3, pady=15)

        # Konsolenausgabe-Feld (nur für Logausgabe)
        self.console_output = tk.Text(root, height=10, wrap='word', bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.console_output.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)
        self.console_output.configure(state='disabled')

        # Logging-Handler für das Text-Widget
        handler = TextHandler(self.console_output)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

        # Standard-Profil setzen
        self.profil_combobox.set("TechnogymEssen1")
        self.profil_auswaehlen()

    def pfad_waehlen(self, entry_widget):
        """ Öffnet einen Dialog zur Auswahl eines Verzeichnisses """
        verzeichnis = filedialog.askdirectory()
        if verzeichnis:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, verzeichnis)

    def profil_auswaehlen(self, event=None):
        """ Setzt die Verzeichnisse anhand des gewählten Profils """
        profil = self.profil_combobox.get()
        if profil in profile_dict:
            for key, entry in self.entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, profile_dict[profil][key])

    def ausfuehren(self):
        """ Startet den Verschiebeprozess in separaten Threads, um die GUI nicht zu blockieren """
        dateipfad1 = self.entries["dateipfad"].get()
        zielverzeichnis1 = self.entries["zielverzeichnis"].get()
        archivverzeichnis1 = self.entries["archivverzeichnis"].get()
        weiteres_zielverzeichnis1 = self.entries["weiteres_zielverzeichnis"].get()

        # Button deaktivieren, Thread starten und nach Abschluss reaktivieren
        self.run_button.config(state='disabled')

        def worker():
            try:
                aufträge_Verschieben(dateipfad1, zielverzeichnis1, archivverzeichnis1, weiteres_zielverzeichnis1)
                logging.info("Verschiebeprozess beendet")
            except Exception:
                logging.exception("Fehler im Verschiebeprozess")
            finally:
                # re-enable button in GUI thread
                self.root.after(0, lambda: self.run_button.config(state='normal'))

        thread1 = threading.Thread(target=worker, daemon=True)
        thread1.start()
        

# Starte GUI
root = tk.Tk()
app = App(root)
root.mainloop()
