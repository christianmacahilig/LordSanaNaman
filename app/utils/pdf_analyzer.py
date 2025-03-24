import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file while maintaining order."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                blocks = page.get_text("blocks")
                blocks.sort(key=lambda b: (b[1], b[0]))  # Sort blocks top-down
                page_text = "\n".join([b[4] for b in blocks])
                print(f"\n=== Page {page_num} ===\n{page_text[:1000]}")  # Debug output
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")

    return text.strip()

def extract_sections(text):
    """Detects and extracts key sections from text."""
    sections = {
        "Title": "",
        "Introduction": "",
        "Objectives": "",
        "Scope and Limitations": ""
    }

    patterns = {
        "Title": r"(?i)^\s*Title\s*[:\-]?\s*(.+)|^(?!Introduction|Objectives|Scope)([A-Z].{5,100})$",
        "Introduction": r"(?i)(Introduction|Rationale|Background of the Study)\s*\n(.*?)(?=\n[A-Z][a-z]|$)",
        "Objectives": r"(?i)(Objectives|Objectives of the Study|Goals|Research Objectives)\s*\n(.*?)(?=\n[A-Z][a-z]|$)",
        "Scope and Limitations": r"(?i)(Scope and Limitations|Scope and Limitations of the Study|Scope of the Study)\s*\n(.*?)(?=\n[A-Z][a-z]|$)"
    }

    for section, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            sections[section] = match.group(2).strip() if match.lastindex == 2 else match.group(1).strip()

    return sections

if __name__ == "__main__":
    pdf_path = "sample.pdf"  # Change this to your actual PDF file path
    extracted_text = extract_text_from_pdf(pdf_path)

    print("\n=== Full Extracted Text ===")
    print(extracted_text[:3000])  # Print first 3000 characters for debugging

    print("\n=== Extracted Sections ===")
    sections = extract_sections(extracted_text)
    for section, content in sections.items():
        print(f"\n**{section}**\n{content[:500]}")  # Print first 500 characters per section
