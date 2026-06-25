"""
Dieses Modul definiert die Klasse ScannedPDF, die für die Verarbeitung gescannter PDF-Dokumente zuständig ist.
Es extrahiert Text mittels OCR und parst relevante Informationen wie Projekt, Auftragsnummer, Referenznummer usw.
"""

import os
import pytesseract
# Relativer Pfad zu tesseract.exe
base_dir = os.path.dirname(os.path.abspath(__file__))
tesseract_path = os.path.join(base_dir, "resources", "Tesseract-OCR", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = tesseract_path
import warnings
import re

warnings.filterwarnings("ignore", category=UserWarning)

class ScannedPDF:
    """
    Klasse zur Repräsentation eines gescannten PDF-Dokuments.
    Extrahiert und speichert Metadaten aus dem PDF-Text.
    """
    def __init__(self, pdf_path, auftragsnummer=None, project=None):
        """
        Initialisiert ein ScannedPDF-Objekt.

        Args:
            pdf_path (str): Pfad zur PDF-Datei.
            auftragsnummer (str, optional): Vorgegebene Auftragsnummer.
            project (str, optional): Vorgegebenes Projekt.
        """
        self.pdf_path = pdf_path  # Speichere den Pfad als Attribut
        contents = self.extract_pdf_text(pdf_path)
        self.project = self.get_project(contents)
        self.auftragsnummer = self.get_auftragsnummer(pdf_path)
        self.referenznummer = self.get_referenznummer(contents)
        self.servicelvl = self.get_servicelvl(contents)
        self.datum = self.get_datum(contents)

    def __repr__(self):
        """
        Gibt eine String-Repräsentation des Objekts zurück.
        """
        return (f"ScannedPDF(project={self.project} \n"
                f"auftragsnummer={self.auftragsnummer} \n"
                f"pdf_path={self.pdf_path}) \n"
                f"referenznummer={self.referenznummer} \n"
                f"servicelvl={self.servicelvl} \n"
                f"datum={self.datum}")

    def extract_pdf_text(self, pdf_path):
        """
        Extrahiert Text aus einer PDF-Datei nur mit Tesseract OCR.
        Optimiert für gescannte PDFs: höhere Skalierung, optionale Vorverarbeitung, flexibler psm.
        """
        text = ""
        try:
            from pypdfium2 import PdfDocument
            pdf = PdfDocument(pdf_path)
            for i, page in enumerate(pdf):
                img = page.render(scale=3).to_pil()  # Höhere Skalierung
                img = img.convert('L')
                ocr_text = pytesseract.image_to_string(
                    img,
                    lang='deu',
                    config='--oem 1 --psm 3'
                )
                text += ocr_text
            pdf.close()
        except Exception as e:
            print(e)
            pass  # Fehler wird ignoriert, das Programm läuft weiter
        return text
    
    def get_project(self, text):
        """
        Ermittelt das Projekt basierend auf Schlüsselwörtern im Text.

        Args:
            text (str): Der extrahierte Text aus der PDF.

        Returns:
            str: Der Projektname oder None.
        """
        if "Vantive" in text:
            return "vantive"
        elif "Gerard" in text:
            return "gerard"
        elif "Gerdts" in text:
            return "gerdts"
        elif "Gocelo" in text:
            return "gocelo"
        elif "Henry" in text:
            return "henry"
        elif "Power" in text:
            return "power"
        elif "Promega" in text:
            return "promega"
        elif "Technogym" in text:
            return "technogym"
        elif "Löwen" in text:
            return "loewen"
        
    def get_auftragsnummer(self, path):
        """
        Extrahiert die Auftragsnummer aus dem Dateinamen (erste 8 Ziffern).

        Args:
            path (str): Pfad zur PDF-Datei.

        Returns:
            str: Die Auftragsnummer oder None.
        """
        filename = os.path.basename(path)
        match = re.match(r'^(\d{8})', filename)
        if match:
            return match.group(1)
        return None
    
    def get_referenznummer(self, text):
        """
        Sucht nach einer Referenznummer im Format 10100XXXXX.

        Args:
            text (str): Der extrahierte Text.

        Returns:
            str: Die Referenznummer oder None.
        """
        match = re.search(r'10100\d{5}', text)
        if match:
            return match.group(0)
        return None
    
    def get_servicelvl(self, text):
        """
        Ermittelt das Servicelevel basierend auf dem Text nach "Servicelevel:".

        Args:
            text (str): Der extrahierte Text.

        Returns:
            str: "Orbi", "Lieferung" oder None.
        """
        keyword = "Servicelevel:"
        keyword_index = text.find(keyword)

        if keyword_index != -1:
            text_after_keyword = text[keyword_index + len(keyword):].strip()
            if text_after_keyword.startswith("O"):
                return "Orbi"
            elif text_after_keyword.startswith("f"):
                return "Lieferung"
            
        return None
    
    def get_datum(self, text):
        """
        Extrahiert das Datum nach dem Schlüsselwort "Entladung".

        Args:
            text (str): Der extrahierte Text.

        Returns:
            str: Das Datum im Format DD.MM.YYYY oder None.
        """
        keyword = "Entladung"
        keyword_index = text.find(keyword)

        if keyword_index != -1:
            text_after_keyword = text[keyword_index + len(keyword):].strip()
            dates = re.findall(r'\d{2}\.\d{2}\.\d{4}', text_after_keyword)
            if dates:
                return dates[0]
        
        return None
    
        
        

# Beispiel für die Nutzung:
#pdf_path = r"X:\Scan aus MAN\Essen\45021732_20260624.pdf"
#scanned_pdf = ScannedPDF(pdf_path)
#text = ScannedPDF.extract_pdf_text(scanned_pdf, pdf_path)
#print(text)
#print(scanned_pdf)