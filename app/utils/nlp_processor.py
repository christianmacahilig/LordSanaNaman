import re
from collections import defaultdict
from utils.csv_loader import load_keywords

def classify_text(text, keywords):
    """Classifies text based on keyword occurrences and scores."""
    cs_score = 0
    it_score = 0
    section_scores = defaultdict(lambda: {"CS": 0, "IT": 0})

    sections = {
        "title": r"(?i)\b(title|topic)\b",
        "introduction": r"(?i)\b(introduction|rationale)\b",
        "objectives": r"(?i)\b(objectives|aims|goals)\b",
        "scope": r"(?i)\b(scope|limitations|boundaries)\b"
    }

    for section, pattern in sections.items():
        if re.search(pattern, text):
            for word in text.split():
                word = word.lower().strip(",.!?")
                if word in keywords["CS"]:
                    section_scores[section]["CS"] += keywords["CS"][word]
                    cs_score += keywords["CS"][word]
                if word in keywords["IT"]:
                    section_scores[section]["IT"] += keywords["IT"][word]
                    it_score += keywords["IT"][word]

    return section_scores, cs_score, it_score

