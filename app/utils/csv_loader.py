import csv

def load_keywords(csv_path):
    keywords = {"CS": {}, "IT": {}}
    
    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                keyword = row["keyword"].strip().lower()
                cs_score = int(row["CS"]) if row["CS"].isdigit() else 0
                it_score = int(row["IT"]) if row["IT"].isdigit() else 0
                
                keywords["CS"][keyword] = cs_score
                keywords["IT"][keyword] = it_score
            except ValueError:
                print(f"❌ Skipping invalid row: {row}")
    
    return keywords
