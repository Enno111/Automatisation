"""
Dieses Modul ist für das Sortieren und Verschieben von PDF-Dateien zuständig.
Es scannt bestimmte Ordner nach PDFs, analysiert sie mit der ScannedPDF-Klasse
und verschiebt sie in entsprechende Zielordner basierend auf Projekt und Auftragsnummer.
Zusätzlich werden Dateien archiviert und bei Bedarf gelöscht.
"""

import os
from pdf import ScannedPDF
import glob
import threading
import shutil
import re

# Dictionary mit den Zielpfaden für verschiedene Projekte
path_dict =  {
    "gerard": r"U:\Aufträge Kunden\Gerard",
    "gerdts": r"U:\Aufträge Kunden\Gerdts",
    "gocelo": r"U:\Aufträge Kunden\Gocelo",
    "henry": r"U:\Aufträge Kunden\Henry Schein",
    "power": r"U:\Aufträge Kunden\Powerplate\Abrechnung",
    "promega": r"U:\Aufträge Kunden\Promega",
    "vantive": r"U:\Aufträge Kunden\Vantive"
}

def main():
    """
    Hauptfunktion des Programms.
    Verarbeitet PDFs aus zwei Quellordnern: Mannheim und Essener Mannheim.
    """
    folder = r"X:\Scan aus MAN\Mannheim"
    pdf_objs = create_scannedpdf_objects_from_folder(folder)
    sort_and_move_pdfs(pdf_objs)
    print("Mannheim Fertig!")

    folder = r"X:\Scan aus ESS\Mannheim"
    pdf_objs = create_scannedpdf_objects_from_folder(folder)
    sort_and_move_pdfs(pdf_objs)
    print("Essener Mannheim Fertig!")

def create_scannedpdf_objects_from_folder(folder_path):
    """
    Erstellt ScannedPDF-Objekte für alle PDF-Dateien in einem Ordner.
    Verwendet Multithreading für parallele Verarbeitung.

    Args:
        folder_path (str): Pfad zum Ordner mit den PDFs.

    Returns:
        list: Liste von ScannedPDF-Objekten.
    """
    pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))
    scanned_objects = []
    threads = []

    def worker(pdf_path):
        """
        Worker-Funktion für einen Thread: Erstellt ein ScannedPDF-Objekt.
        """
        obj = ScannedPDF(pdf_path)
        scanned_objects.append(obj)

    for pdf_path in pdf_files:
        t = threading.Thread(target=worker, args=(pdf_path,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return scanned_objects

def sort_and_move_pdfs(pdf_objs):
    """
    Sortiert und verschiebt die PDF-Objekte in die entsprechenden Zielordner.
    Behandelt spezielle Fälle für bestimmte Projekte.

    Args:
        pdf_objs (list): Liste von ScannedPDF-Objekten.
    """
    archiv_folder = r"X:\Archiv SPA\Mannheim"

    order_dict = {
        "gerard": [],
        "gerdts": [],
        "gocelo": [],
        "henry": [],
        "power": [],
        "promega": [],
        "vantive": [],
        "technogym": [],
        "loewen": []
    }

    for pdf_obj in pdf_objs:
        if not pdf_obj.project:
            continue

        order_dict[pdf_obj.project].append(pdf_obj)
        
        # Spezialbehandlung für loewen: nur ins Archiv verschieben
        if pdf_obj.project == "loewen":
            try:
                dst = os.path.join(archiv_folder, os.path.basename(pdf_obj.pdf_path))
                shutil.copy2(pdf_obj.pdf_path, dst)
                print(f"Loewen archiviert: {pdf_obj.pdf_path} -> {dst}")
                # Lösche die Datei im ursprünglichen Ordner
                if os.path.exists(pdf_obj.pdf_path):
                    os.remove(pdf_obj.pdf_path)
                    print(f"Gelöscht: {pdf_obj.pdf_path}")
            except Exception as e:
                print(f"Fehler bei Loewen: {e}")
            continue
        
        search_folder = path_dict.get(pdf_obj.project)

        if pdf_obj.project == "gocelo" and pdf_obj.auftragsnummer.startswith("68"):
            search_folder = r"U:\Aufträge Kunden\Gocelo\Mannheim\Abrechnung"
        elif pdf_obj.project == "gocelo" and pdf_obj.auftragsnummer.startswith("73"):
            search_folder = r"U:\Aufträge Kunden\Gocelo\Ostfildern"

        auftragsnummer = pdf_obj.auftragsnummer

        if not auftragsnummer or not search_folder:
            continue

        moved = False

        # Suche nach einem passenden Unterordner
        for entry in os.listdir(search_folder):
            entry_path = os.path.join(search_folder, entry)
            if os.path.isdir(entry_path) and auftragsnummer in entry:
                # Verschiebe die PDF in den gefundenen Ordner
                src = pdf_obj.pdf_path
                dst = os.path.join(entry_path, os.path.basename(src))
                try:
                    shutil.move(src, dst)
                    pdf_obj.pdf_path = dst  # Aktualisiere den Pfad im Objekt
                    print(f"Verschoben: {src} -> {dst}")
                    moved = True
                except Exception as e:
                    print(e)
                    pass
                break
        if not moved:
            # Kein Unterordner gefunden, verschiebe direkt in search_folder
            src = pdf_obj.pdf_path
            dst = os.path.join(search_folder, os.path.basename(src))
            try:
                shutil.move(src, dst)
                pdf_obj.pdf_path = dst  # Aktualisiere den Pfad im Objekt
                print(f"Verschoben: {src} -> {dst}")
            except Exception as e:
                print(e)
                pass
        # Kopiere die Datei ins Archiv
        try:
            shutil.copy2(dst, os.path.join(archiv_folder, os.path.basename(dst)))
            print(f"Archiviert: {dst} -> {os.path.join(archiv_folder, os.path.basename(dst))}")
        except Exception as e:
            print(e)
            pass
        # Lösche die Datei im ursprünglichen Ordner
        try:
            if os.path.exists(src):
                os.remove(src)
                print(f"Gelöscht: {src}")
        except Exception as e:
            print(e)
            pass

    # Spezialbehandlung für Henry-Aufträge
    handle_henry(path_dict)
    
    # Ausgabe der sortierten PDFs nach Projekt
    print()
    for project, objs in order_dict.items():
        if objs:
            print(f"\nProjekt: {project}")
            for obj in objs:
                print(f" - {obj.pdf_path} (Auftragsnummer: {obj.auftragsnummer})")

def handle_henry(path_dict):
    """
    Behandelt spezielle Logik für Henry-Aufträge: Verschiebt Ordner zur Abrechnung,
    wenn alle erforderlichen PDFs vorhanden sind.

    Args:
        path_dict (dict): Dictionary mit den Projektpfaden.
    """
    henry_folder = path_dict["henry"]
    for entry in os.listdir(henry_folder):
        entry_path = os.path.join(henry_folder, entry)
        if os.path.isdir(entry_path):
            # Finde alle 8-stelligen Nummern mit 68 am Anfang im Ordnernamen
            matches = re.findall(r"68\d{6}", entry)
            if matches:
                alle_pdfs_vorhanden = True
                for nummer in matches:
                    # Suche nach PDF-Dateien, die mit der Nummer beginnen
                    pdfs = [f for f in os.listdir(entry_path) if f.startswith(nummer) and f.lower().endswith('.pdf')]
                    if not pdfs:
                        alle_pdfs_vorhanden = False
                        break
                if alle_pdfs_vorhanden:
                    abrechnung_ordner = r"U:\Aufträge Kunden\Henry Schein\1. zur Abrechnung"
                    if not os.path.exists(abrechnung_ordner):
                        os.makedirs(abrechnung_ordner)
                    ziel_ordner = os.path.join(abrechnung_ordner, entry)
                    try:
                        shutil.move(entry_path, ziel_ordner)
                        print(f"Henry-Ordner verschoben: {entry_path} -> {ziel_ordner}")
                    except Exception as e:
                        print(e)
                        pass