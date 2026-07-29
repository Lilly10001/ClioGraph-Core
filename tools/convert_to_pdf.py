import sys
import os
from fpdf import FPDF

def py_to_pdf(file_path):
    if not os.path.exists(file_path):
        return

    # PDF-Objekt erstellen
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=10) # Feste Schriftart für Code

    # Datei auslesen und in PDF schreiben
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            pdf.cell(0, 5, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=1)

    # Speicherort festlegen (neben der Originaldatei)
    pdf_path = os.path.splitext(file_path)[0] + ".pdf"
    pdf.output(pdf_path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        py_to_pdf(sys.argv[1])
