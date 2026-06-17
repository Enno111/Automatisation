import pytesseract
from pdf2image import convert_from_path

# Pfad zu Tesseract (nur für Windows notwendig)
pytesseract.pytesseract.tesseract_cmd = r"ressources\Tesseract-OCR\tesseract.exe"

# Pfad zu Poppler (nur für Windows notwendig)
poppler_path = r"ressources\poppler-24.08.0\Library\bin" 

def pdf_zu_text(pdf_pfad):
    """
    Konvertiert eine PDF-Datei in Text mit Hilfe von Tesseract OCR.

    Args:
        pdf_pfad (str): Der Pfad zur PDF-Datei.

    Returns:
        str: Der extrahierte Text aus der PDF-Datei.
    """
    # Konvertiere nur die ersten zwei Seiten der PDF in Bilder
    bilder = convert_from_path(pdf_pfad, first_page=1, last_page=2, poppler_path=poppler_path)

    gesamter_text = ""
    
    for seite, bild in enumerate(bilder):
        text = pytesseract.image_to_string(bild, lang="deu")  # Sprache auf Deutsch setzen
        gesamter_text += f"--- Seite {seite + 1} ---\n{text}\n"

    return gesamter_text