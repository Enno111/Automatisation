"""
Skript zur Erstellung von Ordnern basierend auf E-Mail-Daten.

Dieses Skript analysiert Eingabetext (z.B. aus E-Mails), extrahiert relevante Informationen
wie MKL-Nummer, Bestellnummer, Liefernummer, PLZ und Name, und erstellt automatisch
entsprechende Ordnerstrukturen in den Regionen MA (Mannheim) oder ESS (Essen).
"""

from tkinter import Frame, Label, Text, Button, Scrollbar, NORMAL, DISABLED, END, TOP, BOTTOM, RIGHT, Y
from os import listdir, rename, makedirs
from os.path import join
import sys
from tkinter import Tk
from re import search
# GUI ist vibe-coded

class OutputRedirector:
    """
    Leitet stdout und stderr zum angegebenen Text-Widget um.

    Diese Klasse ermöglicht es, die Konsolenausgabe in ein Tkinter-Text-Widget
    umzuleiten, um die Ausgabe in der GUI anzuzeigen.
    """
    def __init__(self, text_widget):
        """
        Initialisiert den OutputRedirector.

        Args:
            text_widget: Das Tkinter-Text-Widget, in das die Ausgabe geleitet wird.
        """
        self.text_widget = text_widget
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
    
    def write(self, message):
        """
        Schreibt eine Nachricht in das Text-Widget und die Originalausgabe.

        Args:
            message: Die zu schreibende Nachricht.
        """
        self.text_widget.config(state=NORMAL)
        self.text_widget.insert(END, message)
        self.text_widget.see(END)
        self.text_widget.config(state=DISABLED)
        self.original_stdout.write(message)
    
    def flush(self):
        """Flush-Methode für Kompatibilität mit sys.stdout."""
        pass

class Auftrag:
    """
    Repräsentiert einen Auftrag mit extrahierten Informationen aus einem String.

    Diese Klasse analysiert einen Eingabestring
    und extrahiert MKL-Nummer, Bestellnummer, Liefernummer, PLZ, Name und Region.
    """
    def __init__(self, string):
        """
        Initialisiert einen Auftrag aus einem String.

        Args:
            string: Der Eingabestring, der analysiert werden soll.
        """
        self.mkl_nr = search(r"\b(45|68)\d{6}\b", string).group() if search(r"\b(45|68)\d{6}\b", string) else None
        self.order_nr = search(r"\b(10100|20150)\d{5}\b", string).group() if search(r"\b(10100|20150)\d{5}\b", string) else None
        self.delivery_nr = search(r"\b(40100|50100|450\d{2})\d{5}\b", string).group() if search(r"\b(10100|20150)\d{5}\b", string) else None
        self.plz = search(r"\b\d{5}\b", string).group() if search(r"\b\d{5}\b", string) else None

        name_match = search(r"\b\d{5}\b\s*(.+)$", string)
        self.name = name_match.group(1).strip() if name_match else None

        self.region = self.determine_region(plz=self.plz) if self.plz else None

    def determine_region(self, plz):
        """
        Bestimmt die Region basierend auf der Postleitzahl.

        Args:
            plz: Die Postleitzahl als String.

        Returns:
            "MA" für Mannheim oder "ESS" für Essen.
        """
        prefixe = ["6", "54", "55", "56", "35", "36", "97"]

        if any(plz.startswith(p) for p in prefixe):
            return "MA"
        else:
            return "ESS"

class MainWindow:
    """
    Hauptfenster der GUI-Anwendung.

    Diese Klasse erstellt das Hauptfenster mit Eingabefeld, Button und Ausgabefeld.
    Sie verarbeitet die Eingabe und erstellt Ordner basierend auf den extrahierten Daten.
    """
    def __init__(self, master):
        """
        Initialisiert das Hauptfenster.

        Args:
            master: Das Tkinter-Root-Fenster.
        """
        # Oberes Frame für Input
        input_frame = Frame(master)
        input_frame.pack(side=TOP, expand=True, fill="both", padx=10, pady=10)
        
        self.label = Label(input_frame, text="Enter some text:")
        self.label.pack(anchor="nw")

        self.text_entry = Text(input_frame, font=("Arial", 10), height=8)
        self.text_entry.pack(expand=True, fill="both", pady=(5, 10))
        self.text_entry.focus_set()  # Cursor direkt ins Textfeld setzen

        self.button = Button(input_frame, text="Ausführen", command=self.create_folders)
        self.button.pack(pady=5, anchor="se")
        
        # Unteres Frame für Output (Read-Only)
        output_frame = Frame(master)
        output_frame.pack(side=BOTTOM, expand=True, fill="both", padx=10, pady=(0, 10))
        
        output_label = Label(output_frame, text="Output:", font=("Arial", 9, "bold"))
        output_label.pack(anchor="nw")
        
        self.output_text = Text(output_frame, font=("Arial", 9), height=8, state=DISABLED)
        self.output_text.pack(expand=True, fill="both", pady=(5, 0))
        
        # Scrollbar für Output
        scrollbar = Scrollbar(self.output_text)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.output_text.yview)
        
        # Stdout/Stderr umleiten
        self.output_redirector = OutputRedirector(self.output_text)

    mannheim_folder = []  # Liste zur Speicherung der MKL-Nummern für Mannheim-Aufträge

    def create_folders(self):
        """
        Verarbeitet den Eingabetext und erstellt/umbenannt Ordner für jeden Auftrag.

        Diese Methode liest den Text aus dem Eingabefeld, teilt ihn in Zeilen auf,
        erstellt Auftrag-Objekte und ruft create_folder für jeden auf.
        """
        # Stdout/Stderr umleiten
        sys.stdout = self.output_redirector
        sys.stderr = self.output_redirector
        
        try:
            text = self.text_entry.get("1.0", END).strip()
            lines = text.splitlines()
            for line in lines:
                if line.strip():
                    auftrag_obj = Auftrag(line.strip())
                    self.create_folder(auftrag_obj)
            print("\n--- Verarbeitung abgeschlossen ---\n")
            for i in self.mannheim_folder:
                print(i + "\n")
        finally:
            # Stdout/Stderr zurückstellen
            sys.stdout = self.output_redirector.original_stdout
            sys.stderr = self.output_redirector.original_stderr
    

    def create_folder(self, auftrag_obj):
        """
        Erstellt oder benennt einen Ordner für einen Auftrag um.

        Args:
            auftrag_obj: Das Auftrag-Objekt mit den extrahierten Daten.
        """
        zielordner = r"X:\Mannheim\Technogym Digital\3.Mannheim" if auftrag_obj.region == "MA" else r"X:\Mannheim\Technogym Digital\2.Essen-HH"
        nummer = auftrag_obj.order_nr   
        neuer_name = f"{auftrag_obj.mkl_nr}-{auftrag_obj.delivery_nr}-{nummer}-{auftrag_obj.name}-{auftrag_obj.plz}"
        
        gefunden = False

        for ordnername in listdir(zielordner):
            if nummer in ordnername:
                alter_pfad = join(zielordner, ordnername)
                neuer_pfad = join(zielordner, neuer_name)
                if alter_pfad != neuer_pfad:
                    rename(alter_pfad, neuer_pfad)
                    print(f"Ordner umbenannt: {alter_pfad} -> {neuer_pfad}")
                gefunden = True
                break

        if not gefunden:
            neuer_pfad = join(zielordner, neuer_name)
            makedirs(neuer_pfad, exist_ok=True)
            print(f"Ordner erstellt: {neuer_pfad}")

        if auftrag_obj.region == "MA":
            self.mannheim_folder.append(auftrag_obj.mkl_nr)

if __name__ == "__main__":
    # Hauptprogramm: Erstellt das Tkinter-Fenster und startet die GUI-Schleife
    root = Tk()
    root.geometry("800x600")
    app = MainWindow(root)
    root.mainloop() 