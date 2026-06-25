import tesseRACT
import pdfium2
import re

class PDF:
    """
    Eine Klasse zur Verarbeitung von PDF-Dateien.

    Attribute:
        pdf_path (str): Der Pfad zur PDF-Datei.
        servicelvl (str): Der Servicelevel der PDF (z.B. "Orbi" oder "Lieferung").
        referenznummer (int): Die Referenznummer der PDF.
        entladung (list): Eine Liste der Entladungsdaten im Format 'dd.mm.yyyy'.
        auftragsgeber (str): Der Auftragsgeber der PDF (z.B. "Technogym").
        speditionsauftrag (int): Die Speditionsauftragsnummer der PDF.
    """

    def __init__(self, pdf_path):
        """
        Initialisiert die PDF-Klasse mit dem Pfad zur PDF-Datei.

        Args:
            pdf_path (str): Der Pfad zur PDF-Datei.
        """
        self.pdf_path = pdf_path
        self.servicelvl = None
        self.referenznummer = None
        self.entladung = []
        self.auftragsgeber = None
        self.speditionsauftrag = None

        """Initialisierung für die Attribute servicelvl, auftragsnummer und entladung"""

        try:
            # Extrahiere Text aus der PDF-Datei mit pdfium2
            text = pdfium2.pdf_zu_Text(pdf_path)
        except Exception as e:
            print(f"Fehler bei der Verarbeitung mit pdfium2: {e}")
            print("Wechsle zu tesseRACT...")
            text = tesseRACT.pdf_zu_text(pdf_path)

        # Suche nach dem Servicelevel im Text
        keyword = "Servicelevel:"
        keyword_index = text.find(keyword)

        if keyword_index != -1:
            text_after_keyword = text[keyword_index + len(keyword):].strip()
            if text_after_keyword.startswith("O"):
                self.servicelvl = "Orbi"
            elif text_after_keyword.startswith("f"):
                self.servicelvl = "Lieferung"
        else:
            # Wenn der Servicelevel nicht gefunden wurde, versuche es erneut mit tesseRACT
            try:
                text = tesseRACT.pdf_zu_text(pdf_path)
                keyword_index = text.find(keyword)
                if keyword_index != -1:
                    text_after_keyword = text[keyword_index + len(keyword):].strip()
                    if text_after_keyword.startswith("O"):
                        self.servicelvl = "Orbi"
                    elif text_after_keyword.startswith("f"):
                        self.servicelvl = "Lieferung"
            except Exception as e:
                print(f"Fehler bei der Verarbeitung mit tesseRACT: {e}")
        
        # Suche nach dem Entladungsdatum im Text
        keyword = "Entladung"
        keyword_index = text.find(keyword)

        if keyword_index != -1:
            text_after_keyword = text[keyword_index + len(keyword):].strip()
            dates = re.findall(r'\d{2}\.\d{2}\.\d{4}', text_after_keyword)
            self.entladung = dates[:2]

        # Suche nach der Referenznummer im Text
        keyword = "Ref"
        keyword_index = text.find(keyword)

        if keyword_index != -1:
            text_after_keyword = text[keyword_index + len(keyword):].strip()
            referenznummer = re.findall(r'\d{10}', text_after_keyword)
            if referenznummer and referenznummer[0].startswith("10100"):    
                self.referenznummer = int(referenznummer[0])

        # Suche nach dem Auftragsgeber im Text
        keyword = "Technogym"
        keyword_index = text.find(keyword)

        if keyword_index != -1:
            self.auftragsgeber = "Technogym"

        keyword = "Speditionsauftrag"
        keyword_index = text.find(keyword)

        if keyword_index != -1:
            text_after_keyword = text[keyword_index + len(keyword):].strip()
            speditionsauftrag = re.findall(r'\d{8}', text_after_keyword)
            if speditionsauftrag and (speditionsauftrag[0].startswith("450") or speditionsauftrag[0].startswith("681")):    
                self.speditionsauftrag = int(speditionsauftrag[0])

    def __str__(self):
        """
        Gibt eine benutzerdefinierte Zeichenkette zurück, wenn das Objekt gedruckt wird.

        Returns:
            str: Eine Zeichenkette, die die Attribute der PDF-Klasse beschreibt.
        """
        return f"PDF-Objekt:\n  Servicelevel: {self.servicelvl}\n  Speditionsauftrag: {self.speditionsauftrag} \n  Referenznummer: {self.referenznummer}\n  Entladung: {self.entladung} \n  Auftragsgeber: {self.auftragsgeber}"
    

if __name__ == "__main__":
    # Pfad zur Test-PDF anpassen
    TEST_PDF_PATH = r"X:\Scan aus MAN\Essen\45021720_20260624.pdf"

    try:
        pdf = PDF(TEST_PDF_PATH)
        print(pdf)
    except Exception as e:
        print(f"Fehler beim Testen der PDF '{TEST_PDF_PATH}': {e}")