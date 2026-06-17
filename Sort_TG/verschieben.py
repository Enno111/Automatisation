import os
import shutil
from datetime import datetime
import pdfKlasse
import threading
import logging
from pathlib import Path

def getAuftragsnummer(auftrag):
    """
    Extrahiert die Auftragsnummer aus dem Dateinamen.

    Args:
        auftrag (str): Der Dateipfad des Auftrags.

    Returns:
        int: Die Auftragsnummer.
    """
    auftrag_name = os.path.basename(auftrag)
    nummer = auftrag_name[:8]
    if not nummer.isdigit():
        raise ValueError(f"Kein gültiger Auftragsname: {auftrag_name}")
    return int(nummer)

def finde_auftragsordner(auftragsnummer: int, zielverzeichnis: str):
    """
    Findet den passenden Auftragsordner im Zielverzeichnis.

    Diese Funktion durchsucht zuerst das Verzeichnis "2.Essen-HH" und, falls der Auftragsordner dort nicht gefunden wird, das Verzeichnis "3.Mannheim".

    Args:
        auftragsnummer (int): Die Auftragsnummer.
        zielverzeichnis (str): Das Zielverzeichnis, in dem nach dem Auftragsordner gesucht wird.

    Returns:
        str: Der Pfad zum Auftragsordner, falls gefunden, sonst None.
    """
    for ordner in os.listdir(zielverzeichnis):
        if str(auftragsnummer) in ordner:
            return os.path.join(zielverzeichnis, ordner)
    return None  # Falls kein passender Ordner gefunden wurde

# Logger für dieses Modul
logger = logging.getLogger(__name__)

# Lock für Dateioperationen, um Race-Conditions zu vermeiden
file_op_lock = threading.Lock()

def verschiebe_auftrag(auftragsnummer: int, dateipfad: str, zielverzeichnis: str, archiv: str, ordnerZielverzeichnis: str):
    """
    Verschiebt eine Datei in den entsprechenden Auftragsordner.

    Args:
        auftragsnummer (int): Die Auftragsnummer.
        dateipfad (str): Der Pfad zur Datei.
        zielverzeichnis (str): Das Zielverzeichnis.
        archiv (str): Das Archivverzeichnis.
        ordnerZielverzeichnis (str): Das Verzeichnis für erledigte Aufträge.

    Returns:
        str: "L" für Lieferung, "O" für Orbi, "U" für Überprüfen, oder False, wenn der Auftrag nicht verschoben werden konnte.
    """
    # Verwende Pathlib für Pfadoperationen
    ziel_2_essen = Path(zielverzeichnis) / "2.Essen-HH"
    ziel_3_mannheim = Path(zielverzeichnis) / "3.Mannheim"

    auftragsordner = None
    if ziel_2_essen.exists():
        auftragsordner = finde_auftragsordner(auftragsnummer, str(ziel_2_essen))
    if auftragsordner is None and ziel_3_mannheim.exists():
        auftragsordner = finde_auftragsordner(auftragsnummer, str(ziel_3_mannheim))

    auftrag = pdfKlasse.PDF(dateipfad)

    # Stelle sicher, dass das Zielverzeichnis für erledigte Aufträge existiert
    try:
        Path(ordnerZielverzeichnis).mkdir(parents=True, exist_ok=True)
        # auch Standard-Unterordner anlegen
        Path(os.path.join(ordnerZielverzeichnis, "Ueberpruefen")).mkdir(exist_ok=True)
        Path(os.path.join(ordnerZielverzeichnis, "Orbi")).mkdir(exist_ok=True)
    except Exception as e:
        logger.error("Fehler beim Erstellen der Zielverzeichnisse: %s", e)

    try:
        if auftragsordner:
            # Archiv sicherstellen
            Path(archiv).mkdir(parents=True, exist_ok=True)
            # sichere Kopie mit Metadaten
            with file_op_lock:
                shutil.copy2(dateipfad, archiv)

                if len(auftrag.entladung) != 0 and auftrag.servicelvl == "Lieferung":
                    verschiebe_lieferung(auftrag, dateipfad, auftragsordner, ordnerZielverzeichnis)
                    return "L"

                else:
                    shutil.move(dateipfad, auftragsordner)
                    target = Path(ordnerZielverzeichnis) / "Ueberpruefen"
                    target.mkdir(parents=True, exist_ok=True)
                    shutil.move(auftragsordner, str(target))
                    logger.info("%s wurde in Ueberpruefen verschoben", auftragsnummer)
                    return "U"

        elif auftrag.servicelvl == "Orbi" and auftrag.auftragsgeber == "Technogym":
            verschiebe_Orbi(auftrag, dateipfad, archiv, ordnerZielverzeichnis, zielverzeichnis)
            return "O"

        elif auftrag.auftragsgeber == "Technogym":
            Path(archiv).mkdir(parents=True, exist_ok=True)
            with file_op_lock:
                shutil.copy2(dateipfad, archiv)
                target = Path(ordnerZielverzeichnis) / "Ueberpruefen"
                target.mkdir(parents=True, exist_ok=True)
                shutil.move(dateipfad, str(target))
            logger.info("%s wurde in Ueberpruefen verschoben", auftragsnummer)
            return "U"

        else:
            return False

    except Exception as e:
        logger.exception("Der Auftrag %s konnte nicht verschoben werden: %s", auftragsnummer, e)
        return False

def verschiebe_lieferung(auftrag, dateipfad, auftragsordner, ordnerZielverzeichnis):
    """
    Verschiebt eine Datei in den entsprechenden Lieferungs-Auftragsordner.

    Args:
        auftrag (PDF): Das PDF-Objekt des Auftrags.
        dateipfad (str): Der Pfad zur Datei.
        auftragsordner (str): Der Pfad zum Auftragsordner.
        ordnerZielverzeichnis (str): Das Verzeichnis für erledigte Aufträge.

    Returns:
        None
    """
    date = datetime.strptime(auftrag.entladung[-1], "%d.%m.%Y")
    cw = str(date.isocalendar()[1]).zfill(2)
    # verschiebe zuerst die Datei in den Auftragsordner
    with file_op_lock:
        shutil.move(dateipfad, auftragsordner)
        ziel_kw_ordner = Path(ordnerZielverzeichnis) / ("KW" + cw)
        ziel_kw_ordner.mkdir(parents=True, exist_ok=True)
        shutil.move(auftragsordner, str(ziel_kw_ordner))
    logger.info("%s wurde in %s verschoben", auftrag.speditionsauftrag, "KW" + cw)

def verschiebe_Orbi(auftrag, dateipfad, archiv, ordnerZielverzeichnis, zielverzeichnis):
    """
    Verschiebt eine Datei in den entsprechenden Orbi-Auftragsordner.

    Args:
        auftrag (PDF): Das PDF-Objekt des Auftrags.
        dateipfad (str): Der Pfad zur Datei.
        archiv (str): Das Archivverzeichnis.
        ordnerZielverzeichnis (str): Das Verzeichnis für erledigte Aufträge.
        zielverzeichnis (str): Das Zielverzeichnis, in dem nach dem Auftragsordner gesucht wird.

    Returns:
        None
    """
    shutil.copy(dateipfad, archiv)
    
    if auftrag.referenznummer:
        aufragsordner = finde_auftragsordner(auftrag.referenznummer, zielverzeichnis)

        if aufragsordner:
            shutil.move(auftrag.pdf_path, aufragsordner)
            print(f"Orbi: {auftrag.referenznummer} wurde in den passenden Ordner verschoben")
        else:
            shutil.move(dateipfad, ordnerZielverzeichnis + r"\Orbi")
            print(f"Orbi: {auftrag.referenznummer} wurde in {'Orbi'} verschoben")
    else:
        shutil.move(dateipfad, ordnerZielverzeichnis + r"\Orbi")
        print(f"Orbi: {auftrag.referenznummer} wurde in {'Orbi'} verschoben")

def aufträge_Verschieben(dateipfad: str, zielverzeichnis: str, archiv: str, ordnerZielverzeichnis: str):
    """
    Verschiebt alle Aufträge in den passenden Ordner, wenn gefunden.

    Args:
        dateipfad (str): Der Pfad zu den Aufträgen.
        zielverzeichnis (str): Das Zielverzeichnis.
        archiv (str): Das Archivverzeichnis.
        ordnerZielverzeichnis (str): Das Verzeichnis für erledigte Aufträge.

    Returns:
        bool: True, wenn mindestens ein Auftrag erfolgreich verschoben wurde, sonst False.
    """
    aufträge = []

    try:
        aufträge = [os.path.join(dateipfad, f) for f in os.listdir(dateipfad) if os.path.isfile(os.path.join(dateipfad, f))]
    except Exception as e:
        print("Fehler beim Auslesen des Dateipfades")
        print(e)
        return False

    print(f"{len(aufträge)} Aufträge werden bearbeitet")

    verschobeneLieferungen = 0
    verschobeneOrbi = 0
    verschobeneÜberprüfen = 0

    threads = []
    ergebnisse = []

    def thread_function(auftrag_int, auftrag, zielverzeichnis, archiv, ordnerZielverzeichnis, ergebnisse):
        """
        Führt die Funktion verschiebe_auftrag aus und fängt Ausnahmen ab.

        Args:
            auftrag_int (int): Die Auftragsnummer.
            auftrag (str): Der Dateipfad des Auftrags.
            zielverzeichnis (str): Das Zielverzeichnis.
            archiv (str): Das Archivverzeichnis.
            ordnerZielverzeichnis (str): Das Verzeichnis für erledigte Aufträge.
            ergebnisse (list): Liste zur Speicherung der Ergebnisse.

        Returns:
            None
        """
        try:
            ergebnis = verschiebe_auftrag(auftrag_int, auftrag, zielverzeichnis, archiv, ordnerZielverzeichnis)
            ergebnisse.append(ergebnis)
        except Exception as e:
            print(f"Fehler im Thread für Auftrag {auftrag_int}: {e}")
            ergebnisse.append(None)

    for auftrag in aufträge:
        try:
            auftrag_int = getAuftragsnummer(auftrag)
        except ValueError as e:
            print(e)
            continue  # überspringt ungültige Dateien

        try:
            # Erstelle einen Thread für jeden Auftrag
            thread = threading.Thread(target=thread_function, args=(auftrag_int, auftrag, zielverzeichnis, archiv, ordnerZielverzeichnis, ergebnisse))
            threads.append(thread)
            thread.start()

        except Exception as e:
            print("Es ist ein unerwarteter Fehler aufgetreten")
            print(e)

    # Warten Sie, bis alle Threads abgeschlossen sind
    for thread in threads:
        thread.join()

    # Auswertung der Ergebnisse
    for ergebnis in ergebnisse:
        if ergebnis == "L":
            verschobeneLieferungen += 1
        elif ergebnis == "O":
            verschobeneOrbi += 1
        elif ergebnis == "U":
            verschobeneÜberprüfen += 1

    print(f"{os.path.basename(dateipfad)}: Es wurden {verschobeneLieferungen} Lieferungen und {verschobeneOrbi} Orbi-Aufträge verschoben. Dazu müssen {verschobeneÜberprüfen} Aufträge überprüft werden.")
    return True