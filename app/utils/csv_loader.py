import csv

def load_keywords(csv_path):
    """Loads keywords and their scores from a CSV file."""
    keywords = {"CS": {}, "IT": {}}
    with open(csv_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            keyword = row["Keyword"].strip().lower()
            cs_score = int(row["CS_Score"])
            it_score = int(row["IT_Score"])
            keywords["CS"][keyword] = cs_score
            keywords["IT"][keyword] = it_score
    return keywords
