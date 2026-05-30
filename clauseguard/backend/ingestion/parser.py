import os
import fitz  # PyMuPDF
import docx

def parse_pdf(file_path: str):
    """
    Parses a PDF file page by page and returns a list of dictionaries with text, page number.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    pages = []
    doc = fitz.open(file_path)
    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "text": text,
            "page_number": i + 1
        })
    doc.close()
    return pages

def parse_docx(file_path: str):
    """
    Parses a DOCX file and returns simulated page groupings based on paragraph blocks.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    doc = docx.Document(file_path)
    paragraphs = []
    current_page = 1
    char_count = 0
    
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        
        # Approximate page boundary for Word files
        char_count += len(text)
        if char_count > 1500:
            current_page += 1
            char_count = len(text)
            
        paragraphs.append({
            "text": text,
            "page_number": current_page
        })
        
    return paragraphs

def parse_document(file_path: str):
    """
    Unified entrypoint for PDF and DOCX parsing.
    """
    _, ext = os.path.splitext(file_path.lower())
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        return parse_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
