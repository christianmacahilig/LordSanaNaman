import re
import os
import PyPDF2
import fitz  # PyMuPDF (for better extraction)

def get_latest_pdf(upload_folder):
    """Find the most recently uploaded PDF file."""
    pdf_files = [f for f in os.listdir(upload_folder) if f.endswith(".pdf")]
    if not pdf_files:
        print("[ERROR] No PDF files found in the uploads folder.")
        return None
    latest_file = max(pdf_files, key=lambda f: os.path.getmtime(os.path.join(upload_folder, f)))
    return os.path.join(upload_folder, latest_file)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF using PyMuPDF (fallback to PyPDF2 if needed)."""
    text = ""
    
    try:
        # First try using PyMuPDF (more reliable for all PDFs)
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
        
        # If PyMuPDF fails, fallback to PyPDF2
        if not text.strip():
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

    except Exception as e:
        print(f"[ERROR] Failed to extract text: {e}")
        return {}

    return extract_text_sections(text)

def clean_text(text):
    """Cleans and normalizes extracted text."""
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces and newlines
    text = text.replace("- ", "")  # Merge words split by hyphens
    return text.strip()

def extract_title(pdf_text):
    """Extracts the research paper title, ensuring it stops at the Introduction or Abstract."""
    university_header = [
        "Republic of the Philippines",
        "CAVITE STATE UNIVERSITY",
        "Don Severino de las Alas Campus",
        "Indang, Cavite"
        
    ]

    lines = pdf_text.split("\n")
    
    # 1️⃣ Detect University Block
    title_detected = False
    title_index = -1
    for i in range(len(lines) - len(university_header)):
        if all(university_header[j] in lines[i + j] for j in range(len(university_header))):
            title_detected = True
            title_index = i + len(university_header)
            break

    # 2️⃣ Extract Multi-line Title
    extracted_title = []
    if title_detected:
        for i in range(title_index, len(lines)):
            line = lines[i].strip()

            # Stop if we reach Introduction, Abstract, or Table of Contents
            if re.match(r'^(Introduction|Rationale|Abstract|Table of Contents|Chapter|Significance of the Study)', line, re.IGNORECASE):
                break
            
            # Ignore empty lines or page numbers
            if line and not re.match(r'^\d+$', line):
                extracted_title.append(line)

    # 3️⃣ Join Multi-line Title into a Single String
    final_title = " ".join(extracted_title).strip()

    return final_title if final_title else "Title Not Found"

def extract_text_sections(pdf_text):
    """Extracts Title, Introduction, Objectives, and Scope sections reliably."""
    if not isinstance(pdf_text, str):  
        print("[ERROR] Expected a string input for section extraction.")
        return {"title": "", "introduction": "", "objectives": "", "scope": ""}

    sections = {
        "title": extract_title(pdf_text),
        "introduction": "",
        "objectives": "",
        "scope": ""
    }
    
    pdf_text = clean_text(pdf_text)  # Clean the text before processing

    # Extract Introduction
    intro_match = re.search(
        r"(?:Introduction|Rationale|Background)(.*?)(?=\s*(Significance of the Study|Scope and Limitations|Objectives of the Study|Expected Output|References|$))", 
        pdf_text, re.IGNORECASE | re.DOTALL
    )
    
    # Extract Objectives
    # Extract Objectives (More Flexible Matching)
    obj_match = re.search(
        r"(?:Objectives of the Study|General Objective|Specific Objectives|Objectives| O b j e c t i v e s)\s*[:\n]?(.*?)(?=\s*(Scope and Limitations|Significance of the Study|Expected Output|References|$))",
        pdf_text, re.IGNORECASE | re.DOTALL
    )

  
    # Extract Scope and Limitations
    scope_match = re.search(
        r"Scope and Limitations(.*?)(?=\s*(Significance of the Study|Objectives of the Study|Expected Output|References|$))", 
        pdf_text, re.IGNORECASE | re.DOTALL
    )

    # Store extracted sections after cleaning them
    sections["introduction"] = clean_text(intro_match.group(1)) if intro_match else "Introduction Not Found"
    sections["objectives"] = clean_text(obj_match.group(1)) if obj_match else "Objectives Not Found"
    sections["scope"] = clean_text(scope_match.group(1)) if scope_match else "Scope and Limitations Not Found"

    return sections

# Example Usage
if __name__ == "__main__":
    upload_folder = "uploads"  # Change this if needed
    latest_pdf = get_latest_pdf(upload_folder)

    if latest_pdf:
        extracted_data = extract_text_from_pdf(latest_pdf)
        print("\n=== Extracted Sections ===")
        print("Title:", extracted_data["title"])
        print("\nIntroduction:\n", extracted_data["introduction"])
        print("\nObjectives:\n", extracted_data["objectives"])
        print("\nScope and Limitations:\n", extracted_data["scope"])
