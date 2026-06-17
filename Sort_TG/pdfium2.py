import pypdfium2

def pdf_zu_Text(pdf_path):
    """
    Extrahiert den Text aus einer PDF-Datei mit Hilfe von pypdfium2.

    Args:
        pdf_path (str): Der Pfad zur PDF-Datei.

    Returns:
        str: Der extrahierte Text aus der PDF-Datei.
    """
    
    pdf = pypdfium2.PdfDocument(pdf_path)
    text = ""
    try:
        for page_num in range(len(pdf)):
            page = pdf.get_page(page_num)
            textpage = page.get_textpage()
            text += textpage.get_text_bounded()
    finally:
        pdf.close()
    return text