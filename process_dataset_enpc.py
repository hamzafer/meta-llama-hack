import json
import xml.etree.ElementTree as ET

import numpy as np


# Load TMX and extract sentence pairs
def load_tmx(tmx_file):
    tree = ET.parse(tmx_file)
    root = tree.getroot()

    sentence_pairs = []

    for tu in root.findall(".//tu"):
        texts = {}
        for tuv in tu.findall("tuv"):
            lang = tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
            seg = tuv.find("seg").text
            texts[lang] = seg

        if "en" in texts and "nb" in texts:
            sentence_pairs.append({"norwegian": texts["en"], "english": texts["nb"]})

    return sentence_pairs


# Compute dataset statistics
def compute_stats(data):
    en_lengths = [len(pair["norwegian"].split()) for pair in data]
    nb_lengths = [len(pair["english"].split()) for pair in data]

    en_vocab = set(word.lower() for pair in data for word in pair["norwegian"].split())
    nb_vocab = set(word.lower() for pair in data for word in pair["english"].split())

    stats = {
        "Total sentence pairs": len(data),
        "Avg English sentence length": np.mean(en_lengths),
        "Avg Norwegian sentence length": np.mean(nb_lengths),
        "Unique English words": len(en_vocab),
        "Unique Norwegian words": len(nb_vocab)
    }

    return stats


# Save dataset as JSON
def save_json(data, output_file="norges-bank-translations.json"):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ Dataset saved as {output_file}")


# Main Execution
if __name__ == "__main__":
    tmx_file = "norges-bank.no.en-nb.tmx"

    print("🔄 Loading dataset...")
    tmx_data = load_tmx(tmx_file)

    print("📊 Computing statistics...")
    stats = compute_stats(tmx_data)

    for key, value in stats.items():
        print(f"🔹 {key}: {value}")

    save_json(tmx_data)
