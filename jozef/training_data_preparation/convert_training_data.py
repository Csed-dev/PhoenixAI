import json

def convert_to_training_data(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    training_data = [
        {
            "text_input": f"Error: {item['Error']}\nProblematic Code:\n{item['problematic_code']}",
            "output": f"Corrected Code:\n{item['correct_code']}"
        }
        for item in data
    ]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(training_data, f, indent=4)

# Beispielaufruf
convert_to_training_data(".json", ".json")
