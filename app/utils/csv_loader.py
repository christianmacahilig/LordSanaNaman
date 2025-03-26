import csv

def load_keywords(csv_path):
    """Loads CS and IT keywords with their respective scores from a CSV file."""
    keywords = {"CS": {}, "IT": {}}

    try:
        with open(csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    keyword = row.get("keyword", "").strip().lower()
                    cs_score = row.get("CS", "").strip()
                    it_score = row.get("IT", "").strip()

                    # Validate keyword
                    if not keyword:
                        print(f"⚠️ Skipping row due to missing keyword: {row}")
                        continue

                    # Convert scores to integers (default to 0 if invalid)
                    cs_score = int(cs_score) if cs_score.isdigit() else 0
                    it_score = int(it_score) if it_score.isdigit() else 0

                    # Store keyword with scores
                    keywords["CS"][keyword] = cs_score
                    keywords["IT"][keyword] = it_score

                except ValueError as e:
                    print(f"❌ Error processing row {row}: {e}")
                    continue  # Skip bad row

    except FileNotFoundError:
        print(f"❌ [ERROR] CSV file not found: {csv_path}")
    except Exception as e:
        print(f"❌ [ERROR] Unexpected error: {e}")

    return keywords
