import io
import pdfplumber

def extract_text_from_pdf_bytes(pdf_bytes):
    """
    Opens the PDF in memory and extracts text page by page.
    Returns a LIST of strings, where each string is one page.
    """
    page_texts = []
    
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                # Only add the page if it actually contains text
                if text and text.strip():
                    page_texts.append(text.strip())
                    
        if not page_texts:
            print("⚠️ Warning: PDF opened, but no text could be extracted.")
            
        return page_texts
        
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        return []