import pdfplumber

def get_pdf_metadata(pdf_path: str) -> dict:
    with pdfplumber.open(pdf_path) as pdf:
        return {
            "page_count": len(pdf.pages),
            "metadata": pdf.metadata
        }