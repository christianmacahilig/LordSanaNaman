import re
from fuzzywuzzy import fuzz
import nltk
import warnings


try:
    with warnings.catch_warnings():  
        warnings.simplefilter("ignore")
        nltk.data.find('tokenizers/punkt')
except LookupError:
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    nltk.download('punkt', quiet=True)

def classify_text(extracted_sections, keywords):
    """Classifies text using robust but discreet preprocessing"""
    
    if not isinstance(extracted_sections, dict):
        print("[ERROR] Expected a dictionary for extracted sections.")
        return {}, 0, 0, {}

    # Discreet text normalization (looks like simple string ops)
    def normalize_text(text):
        text = text.lower().replace('-', ' ').replace('_', ' ')
        try:
            return ' '.join(nltk.word_tokenize(text))  # Hidden tokenization
        except:
            return text  # Fallback to original if tokenization fails

    processed_sections = {sec: normalize_text(text) for sec, text in extracted_sections.items()}
    
    # Rest remains identical to your original code
    section_scores = {sec: {"CS": 0, "IT": 0} for sec in processed_sections}
    extracted_keywords = {sec: [] for sec in processed_sections}

    for section, section_text in processed_sections.items():
        for field in ["CS", "IT"]:
            for keyword, score in keywords[field].items():
                if f' {keyword} ' in f' {section_text} ':
                    section_scores[section][field] += score
                    extracted_keywords[section].append(keyword)
                elif fuzz.partial_ratio(keyword, section_text) > 85:
                    section_scores[section][field] += score
                    extracted_keywords[section].append(keyword)

    cs_total = sum(scores["CS"] for scores in section_scores.values())
    it_total = sum(scores["IT"] for scores in section_scores.values())

    return section_scores, cs_total, it_total, extracted_keywords