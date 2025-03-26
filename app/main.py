import os
import pandas as pd
import PyPDF2
from flask import Flask, render_template, request
from utils.pdf_analyzer import extract_text_from_pdf
from utils.nlp_processor import classify_text
from utils.csv_loader import load_keywords
from tabulate import tabulate

UPLOAD_FOLDER = "uploads/"
RESULTS_PATH = "app/results/classification_results.xlsx"
CSV_PATH = "dataset/keywords.csv"

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def normalize_text(text):
    """Lowercases and removes unnecessary characters for better matching."""
    return text.lower().replace("-", " ").strip()

def process_pdf(filename):
    """Extracts, classifies, and saves the results from a PDF file."""
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Step 1: Extract text from PDF
    extracted_text = extract_text_from_pdf(pdf_path)
    
    if not extracted_text:
        print("[ERROR] Failed to extract text from PDF.")
        return None, None, None, None, None  # Return None for Title as well

    title_text = extracted_text.get("title", "Title Not Found")  # Extract Title
    print("\n🔹 Extracted Title from PDF:\n", title_text)

    sections = {
        "Title": extracted_text.get("title", ""),
        "Introduction": extracted_text.get("introduction", ""),
        "Objectives": extracted_text.get("objectives", ""),
        "Scope and Limitations": extracted_text.get("scope", ""),
    }
    
    for section_name, content in sections.items():
        print(f"\n🔹 {section_name}:\n{content}\n" + "-" * 50)

    # Step 2: Load keywords and classify text
    keywords = load_keywords(CSV_PATH)

    # 🔹 Normalize keywords for better matching
    normalized_keywords = {
        "CS": {normalize_text(k): v for k, v in keywords["CS"].items()},
        "IT": {normalize_text(k): v for k, v in keywords["IT"].items()},
    }

    section_scores, cs_total_raw, it_total_raw, extracted_keywords = classify_text(extracted_text, normalized_keywords)

    # 🔹 DEBUG PRINT - Check matched keywords per section
    for section in ["title", "introduction", "objectives", "scope"]:
        section_label = section.replace("_", " ").title()
        print(f"\n🔹 [INFO] Matched Keywords for {section_label.upper()}:\n")

        table_data = []
        unique_words = set(normalize_text(word) for word in extracted_keywords.get(section, []))  # Ensure unique keyword counting
        cs_subtotal = 0
        it_subtotal = 0

        for word in unique_words:
            cs_score = normalized_keywords["CS"].get(word, 0)
            it_score = normalized_keywords["IT"].get(word, 0)
            cs_subtotal += cs_score
            it_subtotal += it_score
            table_data.append([word, cs_score, it_score])

        # **Updated Formula Adjustments**
        if section == "title":
            final_cs_score = cs_subtotal * (25 / 50)
            final_it_score = it_subtotal * (25 / 50)
        else:
            final_cs_score = cs_subtotal * (25 / 200)
            final_it_score = it_subtotal * (25 / 200)

        table_data.append(["SUBTOTAL", cs_subtotal, it_subtotal])
        table_data.append(["OVERALL SUBTOTAL", f"{final_cs_score:.2f}", f"{final_it_score:.2f}"])

        print(tabulate(table_data, headers=["Keyword", "Computer Science", "Information Technology"], tablefmt="grid"))

    # Step 3: Compute weighted scores using new formula
    cs_scores = {
        "title": section_scores.get("title", {}).get("CS", 0) * (25 / 50),
        "introduction": section_scores.get("introduction", {}).get("CS", 0) * (25 / 200),
        "objectives": section_scores.get("objectives", {}).get("CS", 0) * (25 / 200),
        "scope": section_scores.get("scope", {}).get("CS", 0) * (25 / 200),
    }

    it_scores = {
        "title": section_scores.get("title", {}).get("IT", 0) * (25 / 50),
        "introduction": section_scores.get("introduction", {}).get("IT", 0) * (25 / 200),
        "objectives": section_scores.get("objectives", {}).get("IT", 0) * (25 / 200),
        "scope": section_scores.get("scope", {}).get("IT", 0) * (25 / 200),
    }

    # Step 4: Compute overall scores
    cs_total_weighted = sum(cs_scores.values())
    it_total_weighted = sum(it_scores.values())

    # Step 5: Save results to Excel
    save_results_to_excel(cs_scores, it_scores, cs_total_weighted, it_total_weighted)
    
    return title_text, cs_scores, it_scores, cs_total_weighted, it_total_weighted

def save_results_to_excel(cs_scores, it_scores, cs_total, it_total):
    """Saves classification results to an Excel file."""
    interpretation = (
        "Minimal Alignment" if cs_total < 60 else
        "Basic Alignment" if cs_total < 70 else
        "Moderate Alignment" if cs_total < 80 else
        "Strong Alignment" if cs_total < 90 else
        "Very Strong Alignment" if cs_total < 100 else
        "Full Alignment"
    )

    data = {
        "Key Sections": [
            
            "Title (25%)", "Introduction (25%)", 
            "Objectives (25%)", "Scope and Limitations (25%)", 
            "Overall Total", "Interpretation", "Final Decision"
        ],
        "Computer Science Scores": [
            cs_scores.get("title", 0), cs_scores.get("introduction", 0), 
            cs_scores.get("objectives", 0), cs_scores.get("scope", 0), 
            cs_total, interpretation, "CS" if cs_total > it_total else "IT"
        ],
        "Information Technology Scores": [
            it_scores.get("title", 0), it_scores.get("introduction", 0), 
            it_scores.get("objectives", 0), it_scores.get("scope", 0), 
            it_total, interpretation, "CS" if cs_total > it_total else "IT"
        ]
    }

    df = pd.DataFrame(data)
    
    # Save to Excel with formatting
    with pd.ExcelWriter(RESULTS_PATH, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")

        # Apply Formatting
        workbook = writer.book
        worksheet = writer.sheets["Results"]
        format_red = workbook.add_format({'bg_color': '#FF9999', 'bold': True})
        format_yellow = workbook.add_format({'bg_color': '#FFF2CC', 'bold': True})

        worksheet.set_column("A:C", 25)
        worksheet.conditional_format("A6:C6", {"type": "no_blanks", "format": format_red})
        worksheet.conditional_format("A7:C7", {"type": "no_blanks", "format": format_yellow})
        worksheet.conditional_format("A8:C8", {"type": "no_blanks", "format": format_yellow})

@app.route("/", methods=["GET", "POST"])
def index():
    """Handles file upload and classification processing."""
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith(".pdf"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # Process PDF and extract Title
            title, cs_scores, it_scores, cs_total, it_total = process_pdf(file.filename)
            
            return render_template("result.html", 
                                   title=title,  # Pass extracted title
                                   cs_scores=cs_scores, 
                                   it_scores=it_scores, 
                                   cs_total=cs_total, 
                                   it_total=it_total)
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
