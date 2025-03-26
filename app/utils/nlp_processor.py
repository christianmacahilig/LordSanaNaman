import re
from fuzzywuzzy import fuzz

def classify_text(extracted_sections, keywords):
    """Classifies text based on predefined CS and IT keywords with proper scoring."""
    
    if not isinstance(extracted_sections, dict):
        print("[ERROR] Expected a dictionary for extracted sections.")
        return {}, 0, 0, {}

    text = " ".join(extracted_sections.values()).lower()  # Convert dict to a single lowercase string

    section_scores = {sec: {"CS": 0, "IT": 0} for sec in extracted_sections}
    extracted_keywords = {sec: [] for sec in extracted_sections}

    for section, section_text in extracted_sections.items():
        section_text = section_text.lower()  # Ensure case-insensitive matching
        
        for keyword, cs_score in keywords["CS"].items():
            if keyword in section_text:
                section_scores[section]["CS"] += cs_score
                extracted_keywords[section].append(keyword)
            elif fuzz.partial_ratio(keyword, section_text) > 85:  # Allow fuzzy matches
                section_scores[section]["CS"] += cs_score
                extracted_keywords[section].append(keyword)

        for keyword, it_score in keywords["IT"].items():
            if keyword in section_text:
                section_scores[section]["IT"] += it_score
                extracted_keywords[section].append(keyword)
            elif fuzz.partial_ratio(keyword, section_text) > 85:
                section_scores[section]["IT"] += it_score
                extracted_keywords[section].append(keyword)

    cs_total = sum(scores["CS"] for scores in section_scores.values())
    it_total = sum(scores["IT"] for scores in section_scores.values())

    return section_scores, cs_total, it_total, extracted_keywords
