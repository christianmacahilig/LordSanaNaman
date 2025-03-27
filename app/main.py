import os
import pandas as pd
from flask import Flask, render_template, request
from utils.pdf_analyzer import extract_text_from_pdf
from utils.nlp_processor import classify_text
from utils.csv_loader import load_keywords
from tabulate import tabulate
from sklearn.metrics import precision_score, recall_score, f1_score  # 
from collections import Counter  
import time
from flask import render_template




UPLOAD_FOLDER = "uploads/"
RESULTS_PATH = "app/results/classification_results.xlsx"
CSV_PATH = "dataset/keywords2.csv"
GROUND_TRUTH_PATH = "dataset/ground_truth.csv"  # ✅ Ensure labeled dataset is available

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def normalize_text(text):
    """Lowercases and removes unnecessary characters for better matching."""
    return text.lower().replace("-", " ").strip()

def load_ground_truth():
    """Loads the ground truth labels from CSV."""
    if os.path.exists(GROUND_TRUTH_PATH):
        return pd.read_csv(GROUND_TRUTH_PATH)
    else:
        print("[WARNING] Ground truth file not found. Evaluation metrics will not be computed.")
        return None

def compute_evaluation_metrics(predicted_labels, actual_labels):
    """Computes Precision, Recall, and F1-score."""
    print(f"Predicted Labels: {predicted_labels}")
    print(f"Actual Labels: {actual_labels}")

    precision = precision_score(actual_labels, predicted_labels, average="macro", zero_division=0)
    recall = recall_score(actual_labels, predicted_labels, average="macro", zero_division=0)
    f1 = f1_score(actual_labels, predicted_labels, average="macro", zero_division=0)

    print("\n📊 Evaluation Metrics:")
    print(f"🔹 Precision: {precision:.4f}")
    print(f"🔹 Recall: {recall:.4f}")
    print(f"🔹 F1-Score: {f1:.4f}")

    if len(set(actual_labels)) < 2:
        print("⚠️ Training Only: Only one class detected in actual labels[ground_truth].")

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

  # First determine the dominant field


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
            final_cs_score = cs_subtotal * (25 / 100)
            final_it_score = it_subtotal * (25 / 100)

        table_data.append(["SUBTOTAL", cs_subtotal, it_subtotal])
        table_data.append(["OVERALL SUBTOTAL", f"{final_cs_score:.2f}", f"{final_it_score:.2f}"])

        print(tabulate(table_data, headers=["Keyword", "Computer Science", "Information Technology"], tablefmt="grid"))

    # Step 3: Compute weighted scores using new formula (with normalization)
    def normalize_score(score):
        """Ensure the maximum score does not exceed 25."""
        return min(score, 25)

    cs_scores = {
        "title": normalize_score(section_scores.get("title", {}).get("CS", 0) * (25 / 50)),
        "introduction": normalize_score(section_scores.get("introduction", {}).get("CS", 0) * (25 / 250)),
        "objectives": normalize_score(section_scores.get("objectives", {}).get("CS", 0) * (25 / 250)),
        "scope": normalize_score(section_scores.get("scope", {}).get("CS", 0) * (25 / 250)),
    }

    it_scores = {
        "title": normalize_score(section_scores.get("title", {}).get("IT", 0) * (25 / 50)),
        "introduction": normalize_score(section_scores.get("introduction", {}).get("IT", 0) * (25 / 250)),
        "objectives": normalize_score(section_scores.get("objectives", {}).get("IT", 0) * (25 / 250)),
        "scope": normalize_score(section_scores.get("scope", {}).get("IT", 0) * (25 / 250)),
    }

    # Sum weighted scores
    cs_total_weighted = sum(cs_scores.values())
    it_total_weighted = sum(it_scores.values())

    final_decision = "CS" if cs_total_weighted > it_total_weighted else "IT"

    # STRICT KEYWORD FILTERING
    strictly_filtered = {}
    for section, words in extracted_keywords.items():
        final_keywords = []
        for word in words:  # Process in original order
            norm_word = normalize_text(word)
            cs_weight = normalized_keywords["CS"].get(norm_word, 0)
            it_weight = normalized_keywords["IT"].get(norm_word, 0)
            
            if final_decision == "CS" and cs_weight == 20 and it_weight == 10:
                final_keywords.append(word)
            elif final_decision == "IT" and cs_weight == 10 and it_weight == 20:
                final_keywords.append(word)
        
        strictly_filtered[section] = final_keywords

    # Create general result by combining all sections
    def get_root_word(word):
        """Enhanced root word normalizer with special cases"""
        word = word.lower().strip()
        
        # Special cases first
        special_cases = {
            'info tech': 'information technology',
            'it': 'information technology',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'algo': 'algorithm',
            'facial recognition':'facial recognition'
        }
        if word in special_cases:
            return special_cases[word]
        
        # Remove plurals and verb forms
        if word.endswith('s') and len(word) > 1:
            word = word[:-1]
        if word.endswith('ing') and len(word) > 3:
            word = word[:-3]
        if word.endswith('es') and len(word) > 2:
            word = word[:-2]
        
        return word

    # In your process_pdf function:
    general_keywords = []
    seen_root_words = set()

    section_order = ['title', 'introduction', 'objectives', 'scope']

    for section in section_order:
        if section in strictly_filtered:
            for word in strictly_filtered[section]:
                norm_word = normalize_text(word)
                root_word = get_root_word(norm_word)
                
                if (root_word not in seen_root_words and 
                    len(general_keywords) < 5 and
                    not any(root_word in kw.lower() for kw in general_keywords) and
                    not any(kw.lower() in root_word for kw in general_keywords)):
                    
                    seen_root_words.add(root_word)
                    # Select the most complete version
                    preferred_forms = {
                        'algorithm': 'algorithms',
                        'machine learning': 'machine learning',
                        'information technology': 'information technology',
                        'face recognition':'facial recognition',
                        'facial recognition':'facial recognition'
                    }
                    
                    display_word = preferred_forms.get(root_word, word)
                    general_keywords.append(display_word)

    # Determine dominant field
    dominant = "Computer Science" if cs_total_weighted > it_total_weighted else "Information Technology"
    target_scores = cs_scores if dominant == "Computer Science" else it_scores

    # Identify weak sections (< 80%)
    low_sections = [
        section.capitalize()
        for section, score in target_scores.items()
        if score < 80
    ]


        # Step 4.1: Identify dominant field and enhancement sections
    final_decision = "CS" if cs_total_weighted > it_total_weighted else "IT"
    final_total = cs_total_weighted if final_decision == "CS" else it_total_weighted
    final_scores = cs_scores if final_decision == "CS" else it_scores

    # Interpretation and enhancement logic
   # Calculate which sections scored low (below thresholds)
    low_threshold = 18 if final_total >= 70 else 20
    enhancement_needed = [k.title() for k, v in final_scores.items() if v < low_threshold]
    all_sections = ['Title', 'Introduction', 'Objectives', 'Scope']
    is_all_sections_weak = len(enhancement_needed) == len(all_sections)

    # Interpretation and enhancement suggestion
    if final_total >= 90:
        interpretation = f"{final_total:.2f}% - Full Alignment (Strong foundation of keywords used)"
        enhancement_suggestion = "None, the use of keywords is strong in this study"

    elif final_total >= 80:
        interpretation = f"{final_total:.2f}% - Strong Alignment (Minor enhancements suggested)"
        enhancement_suggestion = (
            f"Minor change in the following sections: {', '.join(enhancement_needed)}"
            if enhancement_needed else "None, the use of keywords is strong in this study"
        )

    elif final_total >= 70:
        interpretation = f"{final_total:.2f}% - Moderate Alignment (Enhancement needed in key sections)"
        enhancement_suggestion = (
            f"Enhancement needed in the following sections: {', '.join(enhancement_needed)}"
            if enhancement_needed else "None, the use of keywords is fairly solid"
        )

    elif final_total >= 60:
        interpretation = f"{final_total:.2f}% - Basic Alignment (Consider keyword coherence)"
        enhancement_suggestion = (
            "All sections require better keyword relevance"
            if is_all_sections_weak else
            f"Needs a strong foundation in the following sections: {', '.join(enhancement_needed)}"
        )

    elif final_total >= 50:
        interpretation = f"{final_total:.2f}% - Minimal Alignment (Low relevance, improve structure)"
        enhancement_suggestion = (
            "All sections are weak and need improvement"
            if is_all_sections_weak else
            f"Weak areas in: {', '.join(enhancement_needed)}"
        )

    else:
        interpretation = f"{final_total:.2f}% - No Alignment"
        enhancement_suggestion = "Needs a human expert for validation, It has a weak sections."

    # **Evaluation Step: Compare with ground truth**
    # Load the ground truth data
    ground_truth = load_ground_truth()
    if ground_truth is not None:
        # Normalize file title
        clean_filename = normalize_text(os.path.splitext(filename)[0])
        ground_truth["title_normalized"] = ground_truth["title"].apply(normalize_text)

        # Match title
        match = ground_truth[ground_truth["title_normalized"] == clean_filename]

        if not match.empty:
            actual_label = match.iloc[0]["field"]  # Extract the label safely
            predicted_label = "CS" if cs_total_weighted > it_total_weighted else "IT"
            compute_evaluation_metrics([predicted_label], [actual_label])
        else:
            print(f"[WARNING] No ground truth label found for file: {filename}")


    # Step 5: Save results to Excel
    save_results_to_excel(cs_scores, it_scores, cs_total_weighted, it_total_weighted)
    
    print("\n🔹Keywords(Tokenized)  (DEBUG):", extracted_keywords)  # Debugging 
   
   # Flatten keywords for display
    all_keywords = []
    for keyword_list in extracted_keywords.values():
        all_keywords.extend(keyword_list)

    # Remove duplicates and normalize
    flattened_keywords = sorted(set(normalize_text(k) for k in all_keywords))

    

    return title_text, cs_scores, it_scores, cs_total_weighted, it_total_weighted, general_keywords, interpretation, enhancement_suggestion 
    #return title_text, cs_scores, it_scores, cs_total_weighted, it_total_weighted, flattened_keywords, interpretation, enhancement_suggestion



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
        file = request.files.get("file")
        selected_course = request.form.get("selected_course")  #  Get course selection
        print(f"\n✅ Selected Course (from form): {selected_course}\n")

        if file and file.filename.endswith(".pdf"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)



            # Process the uploaded PDF
            title, cs_scores, it_scores, cs_total, it_total, general_keywords, interpretation, enhancement_suggestion= process_pdf(file.filename)

            
            return render_template(
                "result.html",
                title=title,
                cs_scores=cs_scores,
                it_scores=it_scores,
                cs_total=cs_total,
                it_total=it_total,
                extracted_keywords=general_keywords,
                selected_course=selected_course,
                interpretation=interpretation,  
                enhancement_suggestion=enhancement_suggestion,
                
                
        )

        else:
            print("[ERROR] No file uploaded or invalid file type.")
            return render_template("index.html", error="Please upload a valid PDF file.")

    # Render the index page for GET requests
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
