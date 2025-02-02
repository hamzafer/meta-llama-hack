import json

# Load the JSON file
input_file = "norges-bank-translations.json"  # Change this to your actual JSON file name
output_file = "norgesbank-processed.json"

# Define the instruction template
instruction = "Translate the following Norwegian text into English. ONLY OUTPUT the English text and nothing else."

# Read the input JSON file
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Process and convert data
with open(output_file, "w", encoding="utf-8") as f_out:
    for entry in data:
        new_entry = {
            "instruction": instruction,
            "input": entry["norwegian"],  # Norwegian text as input
            "response": entry["english"]  # Expected English translation
        }
        f_out.write(json.dumps(new_entry) + "\n")

print(f"Processed dataset saved to {output_file}")
