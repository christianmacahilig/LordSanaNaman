import pandas as pd
import os

RESULTS_FILE = "C:/Users/ACER/Downloads/THESIS/LordSanaNaman/app/results/classification_results.xlsx"

def save_results_to_excel(title, section_scores, f1_score, recall, precision):
    """Saves classification results into an Excel file without deleting previous entries."""
    
    # Prepare data for saving
    data = {
        "Title": title,
        "Title_CS": section_scores["Title"]["CS_Score"],
        "Title_IT": section_scores["Title"]["IT_Score"],
        "Intro_CS": section_scores["Introduction"]["CS_Score"],
        "Intro_IT": section_scores["Introduction"]["IT_Score"],
        "Objectives_CS": section_scores["Objectives"]["CS_Score"],
        "Objectives_IT": section_scores["Objectives"]["IT_Score"],
        "Scope_CS": section_scores["Scope and Limitations"]["CS_Score"],
        "Scope_IT": section_scores["Scope and Limitations"]["IT_Score"],
        "Total_CS": sum(section["CS_Score"] for section in section_scores.values()),
        "Total_IT": sum(section["IT_Score"] for section in section_scores.values()),
        "F1_Score": f1_score,
        "Recall": recall,
        "Precision": precision
    }

    # Convert to DataFrame
    new_entry = pd.DataFrame([data])

    # Check if file exists
    if os.path.exists(RESULTS_FILE):
        existing_df = pd.read_excel(RESULTS_FILE)
        updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
    else:
        updated_df = new_entry

    # Save to Excel
    updated_df.to_excel(RESULTS_FILE, index=False)
    print(f"Results saved to {RESULTS_FILE} ✅")

