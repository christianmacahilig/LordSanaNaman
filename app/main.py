import os
import pandas as pd
from flask import Flask, render_template, request
from utils.pdf_analyzer import extract_text_from_pdf
from utils.nlp_processor import classify_text
from utils.csv_loader import load_keywords

UPLOAD_FOLDER = "uploads/"
RESULTS_PATH = "app/results/classification_results.xlsx"
CSV_PATH = "dataset/keywords.csv"

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def process_pdf(filename):
    """Extracts, classifies, and saves the results from a PDF file."""
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Extract text
    extracted_text = extract_text_from_pdf(pdf_path)
    
    # Load keywords and classify text
    keywords = load_keywords(CSV_PATH)
    section_scores, cs_total_raw, it_total_raw = classify_text(extracted_text, keywords)

    # Compute weighted scores
    cs_scores = {
        "title": section_scores["title"]["CS"] * 0.25,
        "introduction": section_scores["introduction"]["CS"] * 0.25,
        "objectives": section_scores["objectives"]["CS"] * 0.25,
        "scope": section_scores["scope"]["CS"] * 0.25,
    }

    it_scores = {
        "title": section_scores["title"]["IT"] * 0.25,
        "introduction": section_scores["introduction"]["IT"] * 0.25,
        "objectives": section_scores["objectives"]["IT"] * 0.25,
        "scope": section_scores["scope"]["IT"] * 0.25,
    }

    # Compute overall scores
    cs_total = sum(cs_scores.values())
    it_total = sum(it_scores.values())

    # Save results to Excel
    save_results_to_excel(cs_scores, it_scores, cs_total, it_total)
    
    return cs_scores, it_scores, cs_total, it_total

def save_results_to_excel(cs_scores, it_scores, cs_total, it_total):
    """Saves classification results to an Excel file."""
    data = {
        "Key Sections": [
            "Title (25%)", "Introduction (25%)", 
            "Objectives (25%)", "Scope (25%)", 
            "Overall Total", "Interpretation", "Concluded Result"
        ],
        "Computer Science Scores": [
            cs_scores["title"], cs_scores["introduction"], 
            cs_scores["objectives"], cs_scores["scope"], 
            cs_total, 
            "Well Aligned" if cs_total >= 70 else "Weak Alignment", 
            "CS" if cs_total > it_total else "IT"
        ],
        "Information Technology Scores": [
            it_scores["title"], it_scores["introduction"], 
            it_scores["objectives"], it_scores["scope"], 
            it_total, 
            "Well Aligned" if it_total >= 70 else "Weak Alignment", 
            "CS" if cs_total > it_total else "IT"
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

            # Process PDF
            cs_scores, it_scores, cs_total, it_total = process_pdf(file.filename)
            
            return render_template("result.html", 
                                   cs_scores=cs_scores, 
                                   it_scores=it_scores, 
                                   cs_total=cs_total, 
                                   it_total=it_total)
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
