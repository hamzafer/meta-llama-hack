import json

# Load your JSON file
with open("norges-bank-translations.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert to JSONL format
with open("norges-bank-translations.jsonl", "w", encoding="utf-8") as f:
    for pair in data:
        f.write(json.dumps({"input": pair["english"], "output": pair["norwegian"]}) + "\n")
