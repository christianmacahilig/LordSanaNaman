import re
import PyPDF2
import os

def get_latest_pdf(upload_folder):
    """Find the most recently uploaded PDF file."""
    pdf_files = [f for f in os.listdir(upload_folder) if f.endswith(".pdf")]
    if not pdf_files:
        print("[ERROR] No PDF files found in the uploads folder.")
        return None
    latest_file = max(pdf_files, key=lambda f: os.path.getmtime(os.path.join(upload_folder, f)))
    return os.path.join(upload_folder, latest_file)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file and returns structured sections."""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[ERROR] Failed to extract text: {e}")
        return {}

    return extract_text_sections(text)  # Now correctly returning a dictionary

def extract_text_sections(pdf_text):
    """Extracts Title, Introduction, Objectives, and Scope sections."""
    if not isinstance(pdf_text, str):  
        print("[ERROR] Expected a string input for section extraction.")
        return {"title": "", "introduction": "", "objectives": "", "scope": ""}

    sections = {
        "title": "",
        "introduction": "",
        "objectives": "",
        "scope": ""
    }
    
    lines = pdf_text.split("\n")
    extracted_title = ""

    university_block = [
        "Republic of the Philippines",
        "CAVITE STATE UNIVERSITY",
        "Don Severino de las Alas Campus",
        "Indang, Cavite"
    ]

    title_detected = False
    title_index = -1

    for i in range(len(lines) - len(university_block)):
        if all(university_block[j] in lines[i + j] for j in range(len(university_block))):
            title_detected = True
            title_index = i + len(university_block)
            break

    if title_detected:
        for i in range(title_index, len(lines)):
            line = lines[i].strip()
            if line and not re.match(r'^\d+$', line) and not any(phrase in line for phrase in university_block):
                extracted_title = line
                break

    sections["title"] = extracted_title.strip()
    
    intro_match = re.search(r"(?:Introduction|Rationale|Background)[\s\S]+?(?=Objectives|Scope|$)", pdf_text, re.IGNORECASE)
    obj_match = re.search(r"Objectives[\s\S]+?(?=Scope|Limitations|$)", pdf_text, re.IGNORECASE)
    scope_match = re.search(r"Scope and Limitations[\s\S]+?(?=$)", pdf_text, re.IGNORECASE)

    sections["introduction"] = intro_match.group(0).strip() if intro_match else ""
    sections["objectives"] = obj_match.group(0).strip() if obj_match else ""
    sections["scope"] = scope_match.group(0).strip() if scope_match else ""

    return sections
